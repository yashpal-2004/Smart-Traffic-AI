"""Train/evaluate the Q learner in SUMO; install optional SUMO dependencies first."""
from __future__ import annotations
import argparse
import random
from pathlib import Path

from app.agents.fixed_time import FixedTimeController
from app.agents.q_learning import QLearningAgent, train_episode
from app.evaluation.runner import EpisodeResult, paired_delta_summary, summarize, write_report
from app.simulator.environment import SCENARIOS, SignalConfig
from app.simulator.sumo.environment import SumoEnvironment


def episode(controller, scenario, seed, steps, config, agent=None):
    env=SumoEnvironment(scenario,seed,config,steps)
    fixed=FixedTimeController(min(20,config.max_green),config)
    qsum=0
    try:
        while env.time<steps:
            if controller=='fixed_time': fixed.step(env)
            else:
                action=agent.act(env,explore=False)
                if action: env.request_switch()
                env.step()
            qsum+=sum(env.snapshot().queues.values())
        waits=env.metrics.wait_by_vehicle
        return EpisodeResult(controller,scenario.name,seed,steps,env.metrics.total_arrived,
             env.metrics.total_served,sum(waits)/len(waits) if waits else 0.0,qsum/steps,
             env.metrics.max_total_queue,env.metrics.total_wait_seconds)
    finally: env.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--episodes',type=int,default=100);p.add_argument('--steps',type=int,default=500)
    p.add_argument('--seeds',type=int,nargs='+',default=[101,202,303,404,505])
    p.add_argument('--output',default='backend/artifacts/sumo-evaluation.json')
    args=p.parse_args()
    if args.episodes<1 or args.steps<1:p.error('episodes and steps must be positive')
    scenarios=list(SCENARIOS.values());agent=QLearningAgent();rng=random.Random(2026);config=SignalConfig()
    for _ in range(args.episodes):
        scenario=scenarios[rng.randrange(len(scenarios))]
        agent._rng.seed(rng.randrange(1_000_000))
        env=SumoEnvironment(scenario,rng.randrange(1_000_000),config,args.steps)
        try:train_episode(env,agent,args.steps)
        finally:env.close()
    agent.save('backend/artifacts/sumo_q_table.json')
    rows=[]
    for scenario in scenarios:
        for seed in args.seeds:
            rows.append(episode('fixed_time',scenario,seed,args.steps,config))
            rows.append(episode('q_learning',scenario,seed,args.steps,config,agent))
    by={(r.scenario,r.seed,r.controller):r for r in rows};deltas=[]
    for scenario in scenarios:
        for seed in args.seeds:
            a=by[(scenario.name,seed,'fixed_time')];b=by[(scenario.name,seed,'q_learning')]
            deltas.append({'scenario':scenario.name,'seed':seed,'controller':'q_learning',
                'wait_seconds':round(b.average_wait_seconds-a.average_wait_seconds,3),
                'queue_length':round(b.average_queue_length-a.average_queue_length,3),
                'vehicles_served':b.served-a.served})
    report={'protocol':{'simulator':'Eclipse SUMO via TraCI','paired_seeds':args.seeds,
        'steps_per_episode':args.steps,'training_episodes':args.episodes,
        'scenarios':[s.name for s in scenarios],'training_data_excluded':True,
        'wait_definition':'Mean accumulated vehicle waiting time among vehicles arriving at their destination.',
        'queue_definition':'Mean halted vehicles counted across the four inbound lanes per simulation step.'},
        'summary':summarize(rows),'paired_deltas_vs_fixed_time':deltas,
        'paired_summary_vs_fixed_time':paired_delta_summary(deltas),
        'episodes':[r.__dict__ for r in rows]}
    write_report(report,args.output)
    print(f"Saved SUMO evaluation to {args.output}")
    for name,m in report['summary'].items():
        print(f"{name}: wait={m['average_wait_seconds']['mean']:.2f}s queue={m['average_queue_length']['mean']:.2f} served={m['vehicles_served']['mean']:.1f}")

if __name__=='__main__': main()
