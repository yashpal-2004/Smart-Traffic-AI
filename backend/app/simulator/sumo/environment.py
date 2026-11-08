"""SUMO/TraCI adapter exposing the queue state expected by the Q-learning agents."""
from __future__ import annotations
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from statistics import mean
from dataclasses import dataclass, field

from app.simulator.environment import Approach, Phase, Scenario, SignalConfig, Snapshot

SUMO_DIR = Path(__file__).resolve().parent


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
                 sumo_binary: str = "sumo", amber_seconds: int | None = None):
        try:
            import traci
        except ImportError as exc:
            raise RuntimeError("SUMO support is optional. Install with python -m pip install -r backend/requirements-sumo.txt") from exc
        binary = _binary(sumo_binary)
        if not binary:
            raise RuntimeError(f"{sumo_binary} not found. Install SUMO and ensure its bin directory is on PATH.")
        self.traci, self.scenario, self.seed, self.config = traci, scenario, seed, config
        self.sumo_binary, self._requested_amber = sumo_binary, amber_seconds
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
        try:
            # SUMO can take a few seconds to initialize on its first launch,
            # especially when installed from the Python package on macOS.
            self.traci.start(command,label=self._connection_label,numRetries=30)
            self.conn=self.traci.getConnection(self._connection_label)
            self.conn.trafficlight.setRedYellowGreenState("center", "GGrr")
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

    @property
    def transitioning(self): return self._amber_remaining>0

    def _signal(self):
        if self.phase==Phase.NORTH_SOUTH:
            state='yyrr' if self.transitioning else 'GGrr'
        else:
            state='rryy' if self.transitioning else 'rrGG'
        self.conn.trafficlight.setRedYellowGreenState("center",state)

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

    def step(self, switch=False):
        if switch:
            self.request_switch()
        self.conn.simulationStep()
        departed=self.conn.simulation.getDepartedIDList()
        arrived=self.conn.simulation.getArrivedIDList()
        for vehicle in departed: self._wait_by_id[vehicle]=0
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
        sumo_binary, amber = self.sumo_binary, self._requested_amber
        self.close()
        self.__init__(scenario, seed, config, steps, sumo_binary, amber)
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
