# Product, Pages, and Premium UI Direction

## Information architecture
Single-page application with four primary sections: **Simulate**, **Compare**, **Learn**, and **About**. Keep global scenario and run controls easy to reach.

### Simulate page (primary)
- Header: project name, scenario selector, Run/Pause, Step, Reset.
- Main canvas: four-way intersection, animated vehicles, explicit red/amber/green signal indicators, queue count per approach, crossing direction arrows.
- Side panel: controller (Fixed-time / RL), current phase, elapsed simulation time, agent action, concise reason derived from observable state (e.g. “North queue is longest”).
- Metric strip: waiting time, total queue, vehicles served, episode time.
- Lower panel: live queue/wait chart and an expandable “How the agent decides” explanation.

### Compare page
- Run matched evaluation batches for fixed-time and trained RL policies.
- Clearly state seed count and traffic scenarios. Show mean and spread, not only a best run.
- Charts for average wait, throughput, queue length; include a compact results table and export JSON/CSV.
- Do not imply statistical significance without an appropriate analysis.

### Learn page
- Explain environment, state, actions, reward, Q-learning, exploration vs exploitation, and limitations.
- Show a small state/action/reward trace from an actual run.
- Glossary/tooltips for ML terms.

### About page
- Project purpose, assumptions, limitations, links to source and documentation.

## Visual direction
Premium technical control-room aesthetic: deep ink/navy canvas, warm near-white text, restrained electric teal for active/data states, amber for caution, coral/red for stop/error. Use generous spacing, strong typography hierarchy, crisp borders, subtle shadows, and purposeful motion. Keep charts and controls calm; avoid noisy gradients, glass effects everywhere, emoji icons, or decorative animations that obscure data.

## Interaction and states
- First-load guided empty state with “Run demo scenario”.
- Running, paused, stepping, completed, error, and training states are visually distinct.
- Disable incompatible controls while a run is active and explain why.
- Reduced-motion mode; animation must not be the only way to understand state.
- Responsive: desktop-first visualization; mobile uses stacked metrics and a simplified top-down intersection.

## Accessibility
Keyboard-operable controls, visible focus, semantic labels, sufficient contrast, color-independent signal labels/icons, chart text summaries, and reduced motion support.

## UI quality bar
Every page must have a clear hierarchy, aligned spacing, consistent control sizing, readable empty/loading/error states, responsive behavior, and real data. Avoid placeholder charts and fake “AI insight” copy.
