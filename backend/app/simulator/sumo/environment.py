"""SUMO/TraCI adapter exposing the queue state expected by the Q-learning agents."""
from __future__ import annotations
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from statistics import mean
from dataclasses import dataclass, field

from app.simulator.environment import Approach, Phase, Scenario, SignalConfig, Snapshot

SUMO_DIR = Path(__file__).resolve().parent
SUMO_ENVIRONMENT_VERSION = 3  # includes link ordering and delayed-departure queues


def _binary(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    try:
        import sumo
        candidate = Path(sumo.SUMO_HOME) / "bin" / name
        return str(candidate) if candidate.is_file() else None
    except ImportError:
        return None


def sumo_gui_status() -> tuple[bool, str | None]:
    if not _binary("sumo-gui"):
        return False, "The sumo-gui executable was not found."
    if sys.platform == "darwin":
        xquartz_installed = (Path("/Applications/Utilities/XQuartz.app").exists()
                             or Path("/opt/X11").exists())
        if not xquartz_installed:
            return False, "SUMO's desktop viewer on macOS requires XQuartz. Install XQuartz, open it once, then restart the backend."
        if not os.environ.get("DISPLAY"):
            return False, "Open XQuartz and restart the backend so SUMO can connect to its display."
    elif sys.platform.startswith("linux") and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False, "SUMO's desktop viewer needs an active graphical display."
    return True, None


def prepare_network(target: Path) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    net = target / "traffic.net.xml"
    if net.exists():
        return net
    netconvert = _binary("netconvert")
    if not netconvert:
        raise RuntimeError("SUMO netconvert is missing. Install eclipse-sumo (see requirements-sumo.txt).")
    args = [netconvert, "--node-files", str(SUMO_DIR / "traffic.nod.xml"),
            "--edge-files", str(SUMO_DIR / "traffic.edg.xml"), "--connection-files",
            str(SUMO_DIR / "traffic.con.xml"), "--output-file", str(net), "--no-turnarounds", "true"]
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(f"netconvert failed: {result.stderr.strip()}")
    return net


class SumoEnvironment:
    def __init__(self, scenario: Scenario, seed: int, config: SignalConfig, steps: int,
                 sumo_binary: str = "sumo", amber_seconds: int | None = None, gui: bool = False):
        try:
            import traci
        except ImportError as exc:
            raise RuntimeError("SUMO support is optional. Install with python -m pip install -r backend/requirements-sumo.txt") from exc
        binary_name = "sumo-gui" if gui else sumo_binary
        binary = _binary(binary_name)
        if not binary:
            raise RuntimeError(f"{binary_name} not found. Install SUMO and ensure its bin directory is on PATH.")
        if gui:
            available, message = sumo_gui_status()
            if not available:
                raise RuntimeError(message or "SUMO's desktop viewer is unavailable.")
        self.traci, self.scenario, self.seed, self.config = traci, scenario, seed, config
        self.sumo_binary, self._requested_amber, self.gui = sumo_binary, amber_seconds, gui
        self.steps_limit = steps
        self.time = self.phase_elapsed = 0
        self.phase = Phase.NORTH_SOUTH
        self._amber_remaining = 0
        self._pending_phase = None
        self.amber_seconds = amber_seconds or config.amber_seconds
        @dataclass
        class Metrics:
            total_arrived: int = 0
            total_served: int = 0
            total_wait_seconds: int = 0
            max_total_queue: int = 0
            wait_by_vehicle: list[float] = field(default_factory=list)
            @property
            def average_wait_seconds(self):
                return mean(self.wait_by_vehicle) if self.wait_by_vehicle else 0.0
        self.metrics=Metrics()
        self.queues = {a: [] for a in Approach}
        self._wait_by_id = {}
        self._pending_wait_by_id = {}
        self._last_departed=set()
        self._temp=tempfile.TemporaryDirectory(prefix="traffic-sumo-")
        work=Path(self._temp.name)
        prepare_network(work)
        route_file=work/"demand.rou.xml"
        route_file.write_text(self._routes(),encoding="utf-8")
        self._connection_label=f"signal_lab_{os.getpid()}_{id(self)}"
        command=[binary,"-c",str(SUMO_DIR/"traffic.sumocfg"),"--net-file",str(work/"traffic.net.xml"),
                 "--route-files",str(route_file),"--seed",str(seed),"--end",str(steps),
                 "--no-step-log","true","--duration-log.disable","true"]
        if gui:
            command.append("--start")
        try:
            # SUMO can take a few seconds to initialize on its first launch,
            # especially when installed from the Python package on macOS.
            self.traci.start(command,label=self._connection_label,numRetries=30)
            self.conn=self.traci.getConnection(self._connection_label)
            self._build_signal_link_map()
            self._signal()
        except Exception:
            self._temp.cleanup()
            raise

    def _routes(self):
        rates={a.value:r for a,r in self.scenario.arrival_rates.items()}
        routes={'north':'north_in south_out','south':'south_in north_out','east':'east_in west_out','west':'west_in east_out'}
        flows=[]
        for name,edges in routes.items():
            rate=rates[name]
            if rate<=0: continue
            flows.append(f'<flow id="flow_{name}" type="car" route="route_{name}" begin="0" end="{self.steps_limit}" probability="{rate:.6f}" departLane="best" departSpeed="max"/>')
        route_xml=''.join(f'<route id="route_{name}" edges="{edges}"/>' for name,edges in routes.items())
        return '<routes><vType id="car" accel="2.6" decel="4.5" length="5" maxSpeed="13.89"/> '+route_xml+''.join(flows)+'</routes>'

    def _build_signal_link_map(self):
        links = self.conn.trafficlight.getControlledLinks("center")
        self._signal_link_count = len(links)
        self._signal_link_approach = {}
        for index, connections in enumerate(links):
            approaches = {
                incoming.split("_in_", 1)[0]
                for incoming, _, _ in connections
                if "_in_" in incoming
            }
            if len(approaches) == 1:
                self._signal_link_approach[index] = approaches.pop()
        found = set(self._signal_link_approach.values())
        required = {approach.value for approach in Approach}
        if found != required:
            raise RuntimeError(f"SUMO signal links do not cover all approaches: {sorted(found)}")

    @property
    def transitioning(self): return self._amber_remaining>0

    def _signal(self):
        active = {"north", "south"} if self.phase == Phase.NORTH_SOUTH else {"east", "west"}
        color = "y" if self.transitioning else "G"
        state = "".join(color if self._signal_link_approach.get(index) in active else "r"
                        for index in range(self._signal_link_count))
        self.conn.trafficlight.setRedYellowGreenState("center", state)

    def request_switch(self):
        if self.transitioning or self.phase_elapsed<self.config.min_green: return False
        self._pending_phase=Phase.EAST_WEST if self.phase==Phase.NORTH_SOUTH else Phase.NORTH_SOUTH
        self._amber_remaining=self.amber_seconds
        self._signal()
        return True

    def snapshot(self):
        result={}
        for approach,edge in ((Approach.NORTH,"north_in"),(Approach.SOUTH,"south_in"),(Approach.EAST,"east_in"),(Approach.WEST,"west_in")):
            lane=f"{edge}_0"
            result[approach]=self.conn.lane.getLastStepHaltingNumber(lane)
        for vehicle_id in self.conn.simulation.getPendingVehicles():
            approach_name = vehicle_id.split(".", 1)[0].removeprefix("flow_")
            try:
                result[Approach(approach_name)] += 1
            except ValueError:
                continue
        self.queues={a:[None]*n for a,n in result.items()}
        return Snapshot(
            time=self.time,
            phase=self.phase,
            transitioning=self.transitioning,
            phase_elapsed=self.phase_elapsed,
            queues=result,
            arrived=self.metrics.total_arrived,
            served=self.metrics.total_served,
            total_wait_seconds=self.metrics.total_wait_seconds,
            average_wait_seconds=self.metrics.average_wait_seconds,
            max_total_queue=self.metrics.max_total_queue,
        )

    def visualization(self):
        """Return live world coordinates for the browser's SUMO network view."""
        vehicles = []
        for vehicle_id in self.conn.vehicle.getIDList():
            x, y = self.conn.vehicle.getPosition(vehicle_id)
            vehicles.append({
                "id": vehicle_id,
                "x": round(x, 2),
                "y": round(y, 2),
                "angle": round(self.conn.vehicle.getAngle(vehicle_id), 1),
                "speed": round(self.conn.vehicle.getSpeed(vehicle_id), 2),
            })
        (min_x, min_y), (max_x, max_y) = self.conn.simulation.getNetBoundary()
        junction_shape = self.conn.junction.getShape("center")
        junction_bounds = {
            "min_x": min(point[0] for point in junction_shape),
            "max_x": max(point[0] for point in junction_shape),
            "min_y": min(point[1] for point in junction_shape),
            "max_y": max(point[1] for point in junction_shape),
        }
        signal_state = self.conn.trafficlight.getRedYellowGreenState("center")
        signal_states = {
            approach: signal_state[index]
            for index, approach in self._signal_link_approach.items()
        }
        return {
            "vehicles": vehicles,
            "signal_state": signal_state,
            "signal_states": signal_states,
            "network_bounds": {
                "min_x": min_x, "max_x": max_x,
                "min_y": min_y, "max_y": max_y,
            },
            "junction_bounds": junction_bounds,
        }

    def step(self, switch=False):
        if switch:
            self.request_switch()
        pending_before_step = self.conn.simulation.getPendingVehicles()
        for vehicle_id in pending_before_step:
            self._pending_wait_by_id[vehicle_id] = self._pending_wait_by_id.get(vehicle_id, 0) + 1
        self.conn.simulationStep()
        departed=self.conn.simulation.getDepartedIDList()
        arrived=self.conn.simulation.getArrivedIDList()
        for vehicle in departed:
            self._wait_by_id[vehicle] = self._pending_wait_by_id.pop(vehicle, 0)
        for vehicle in self.conn.vehicle.getIDList():
            if self.conn.vehicle.getSpeed(vehicle) < 0.1:
                self._wait_by_id[vehicle] = self._wait_by_id.get(vehicle, 0) + 1
        for vehicle in arrived:
            self.metrics.wait_by_vehicle.append(self._wait_by_id.pop(vehicle, 0))
        self.metrics.total_arrived+=len(departed);self.metrics.total_served+=len(arrived)
        self.time+=1
        if self.transitioning:
            self._amber_remaining-=1
            if self._amber_remaining==0:self.phase=self._pending_phase;self._pending_phase=None;self.phase_elapsed=0
        else:self.phase_elapsed+=1
        self._signal()
        snap=self.snapshot();queue=sum(snap.queues.values())
        self.metrics.total_wait_seconds+=queue;self.metrics.max_total_queue=max(self.metrics.max_total_queue,queue)
        return snap

    def reset(self):
        scenario, seed, config, steps = self.scenario, self.seed, self.config, self.steps_limit
        sumo_binary, amber, gui = self.sumo_binary, self._requested_amber, self.gui
        self.close()
        self.__init__(scenario, seed, config, steps, sumo_binary, amber, gui)
        return self.snapshot()

    def close(self):
        try:
            conn = getattr(self, "conn", None)
            if conn is not None:
                process = getattr(conn, "_process", None)
                conn.close(wait=False)
                if process is not None:
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
        finally:
            self._temp.cleanup()
