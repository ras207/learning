# Problem model: Permanent Learning System

Iteration 1 · produced by `model-problem` · 2026-09-25 · updated 2026-09-25 with the user's answers to WI-011 and WI-012

Inputs: intent model `art-intent-model`, ambition map `art-ambition-map`, current evaluations G1-E1 and G2-E1, decisions D-001 to D-003, and the user's answers in the 2026-09-25 sitting to WI-003 (purpose and why now), WI-005 with WI-010 (constraints and openness) and WI-002 (starting point and target capabilities).

Labels: **[stated]** means the user said it directly. **[inference]** is the agent's reading, open to correction. **[general knowledge]** is widely accepted learning-science or practice knowledge that the agent applies here; it has not been researched or verified for this project. **[assumption]** is a working proposition recorded in state and still to be confirmed. The model describes the problem and does not assume that a "system" of any kind is the answer.

## 1. Problem statement (solution-independent)

An experienced economist wants to spend years building an unusual combination of capabilities: deep economics, the ability to build and validate AI-driven analytical systems, and the commercial and relationship skills to sell insight. The aim is to deliver genuinely useful advice, and eventually to run their own business. **[stated]**

The way they learn now does not reliably turn limited, fragmented time into that capability. It is not interactive, it does not keep up with fast-moving fields, and it does not adapt to their strengths and weaknesses as a learner. **[stated]** No existing course or programme covers the intersection they are aiming at. **[inference]** They also want to keep their own reasoning and judgement strong, and not hand them to AI. **[stated, B1]**

In short: **turning about seven hours a week, over many years, into demonstrable, current, integrated capability at the intersection of economics, AI systems and advisory business, without losing ownership of one's own thinking.**

## 2. Who is affected and how

| Party | How they are affected | Basis |
|---|---|---|
| **The user** (primary, sole learner) | Economist, five years leading a small team that gives independent advice to government, after a year in consulting. Holds a master's in economics. Has done six months of unstructured learning about AI. Has never run a business. Feels their current learning is not interactive, not current and not tailored. | [stated] |
| **The user's team and government clients** (indirect) | They benefit if the user's analytical and AI capability grows. The workplace is a real venue for learning, but the AI tools available there are extremely limited. | [stated] venue and tools; [inference] benefit |
| **Future clients of the user's business** (indirect, future) | The business is independent policy advice, so these are future policy clients. Their eventual value depends on capability built now. They are not users of anything in scope. | [stated] business form; [inference] otherwise; consistent with D-003 and deferred WI-009 |
| **People as sources of challenge and feedback** (AM-5) | Academic economists, senior officials, mentors and peers are both where the user must eventually perform and the most credible judges of their capability. The user's default is privacy, so feedback comes through private channels, not an audience. | [stated] targets and privacy; [inference] role |

## 3. Starting point and target capability

**Starting point.** Strong in applied economics and advisory practice, managing a team, and working with government. Theory and econometrics need a refresh. Early and unstructured in AI. Some coding (R, some Python). No software engineering discipline yet, and no business experience. **[stated; the coding level was stated by the user outside the ideation sittings]**

| Horizon | Target capability, in the user's words | Nature of the gap **[inference]** |
|---|---|---|
| ~1 year | Set up and run automated agentic workflows. Refresh economic theory and econometrics. Begin to understand how to build good software. | A new technical practice, plus refreshing existing depth. Both need hands-on practice and feedback, not content. |
| ~3 years | Develop and validate agentic systems that produce robust economic analysis. Converse credibly with academic economists and senior officials about policy. Sell valuable insights. | Integration across domains. "Validate" and "robust" demand methodological judgement, which is exactly what B1 protects. Selling is a new capability with no current practice. |
| 10+ years | A respected advisor on key policy issues, with wide understanding of economics, financial markets and technology, delivering influential insights that improve policy. | Breadth, judgement and reputation. "Respected" and "influential" depend partly on how others perceive the user, not only on ability. |

**Observation [inference]: the two halves of the trajectory draw on different time.** Economics and advisory capability can be practised at work, on real problems, with stakes. The AI-systems half has almost no outlet at work, so it depends mostly on the roughly seven personal hours a week. Integrating the two, meaning AI-enabled economic analysis, has no natural venue at present. It must be created in personal time or through work outside the day job. This sharpens M6 and M10.

**Observation [inference].** The targets form one coherent trajectory, not a set of scattered interests: economics depth, then AI-enabled analysis, then advisory influence and business. This matters for the problem. The hard part is less "learn many subjects" and more **integration**: building capabilities that are valuable because they are combined, and that no external curriculum assembles.

## 4. Mechanisms: why capability is not developing as wanted

| ID | Mechanism | Basis |
|---|---|---|
| M1 | **Content without practice and feedback.** Reading, watching and courses produce familiarity. Capability comes from effortful retrieval, practice on realistic problems and timely feedback. The user's "not interactive" is this gap. | [stated] symptom; [general knowledge] mechanism |
| M2 | **No persistent picture of the learner.** Nothing remembers what the user has mastered, where they go wrong, or how they learn best. Each session starts cold, so tailoring is impossible and effort goes to the wrong places. | [stated] "not tailored"; [inference] cause |
| M3 | **Fast-moving fields make static material stale.** AI practice changes in months. Economics and policy debates move too. Fixed curricula and older content lag, and choosing *what* is worth learning is itself a moving target (AM-4). | [stated] "not responsive to advances"; [inference] |
| M4 | **Unstructured self-direction lacks sequencing and calibration.** Six months of unstructured AI learning gives exposure, but no reliable sense of what is known, what comes next, or whether it has stuck. | [stated] unstructured; [inference] effect |
| M5 | **Learning sits apart from real use.** Capability that is never applied to a consequential problem transfers poorly and is hard to demonstrate (B4, B6). The day job is a real venue for consequential practice in economics, advice and judgement. However, the AI tools available there are extremely limited, so it offers little AI practice (A-006). | [general knowledge]; [stated] venue and tools |
| M6 | **Fragmented time.** About seven hours a week. Weekdays are short slots around a commute, and weekends have longer blocks. Project-based learning needs continuity and longer blocks. Short slots lose context unless something carries it between sessions. | [stated] time; [inference] effect; [assumption] A-005 |
| M7 | **Decay without maintenance.** Skills not used fade, and the econometrics refresh shows this has already happened once. Over a decade, keeping capabilities matters as much as gaining them (AM-10). | [stated] "refresh"; [general knowledge] |
| M8 | **AI assistance can hollow out capability.** The tools that make interactive, current learning cheap can also do the thinking. Output then improves while the user's own reasoning does not. This is the core risk behind B1, and it is sharpest for "validate" and "robust" in the three-year target. | [stated] B1; [inference] mechanism |
| M9 | **Sustaining effort over years.** Permanence depends on motivation and habit surviving work pressure, life changes and plateaus. Most self-directed programmes fade. | [inference]; WI-006 |
| M10 | **Meta-work competes for the same hours.** Any time spent designing, building or tending how one learns comes from the seven hours. D-002 turns part of this into learning, because building AI workflows and good software are one-year targets. Upkeep and tinkering that do not build target capability remain pure cost, and economics could be starved while the technical work absorbs time. | [inference]; WI-006, D-002 |

## 5. Current approaches and why each falls short

| Approach | What it does well | Why it is inadequate here |
|---|---|---|
| Courses, MOOCs, books, videos | Structured content, often high quality | Not interactive (M1), not tailored (M2), often lag the frontier (M3), no connection across domains, and produce completion rather than demonstrable capability (B2). **[stated/inference]** |
| Unstructured learning with AI chat (the user's last six months) | Interactive, current, on demand | Nothing persists between sessions (M2), no sequencing or assessment (M4), and it easily does the thinking for the user (M8). **[stated/inference]** |
| Formal study (for example a further degree) | Depth, credentials, academic network | Expensive, slow, a fixed curriculum, poorly matched to seven hours a week, and weighted toward credentials (B2). It may still serve credibility for the 10-year goal (A-003 challenge). **[inference]** |
| Learning on the job | Real stakes and real feedback. The user confirms work is somewhere they could learn. | Limited to what the role demands. AI tools at work are extremely limited, so it is weak on AI engineering, and weak on running a business. **[stated/inference]** |
| Mentors, coaches, tutors | Tailored challenge and credible judgement | Costly or intermittent, and hard to find at this intersection. They remain valuable as sources of evidence (AM-5). **[inference]** |
| Spaced repetition and note systems | Retention and a personal knowledge base | Maintain knowledge rather than build applied capability. They do no diagnosis or sequencing. Heavy setups themselves invite meta-work (M10). **[general knowledge/inference]** |
| Commercial AI tutors | Interactive and somewhat adaptive | Generic curricula, usually held by the provider (conflicts with privacy and AM-3), rarely lifelong or cross-domain. **[inference, not researched]** |

## 6. Why the current state is inadequate (summary)

No current approach combines **interaction and feedback**, **a persistent picture of the learner**, **currency with fast-moving fields**, **integration across the user's specific domains**, **grounding in consequential work** and **protection of the user's own reasoning**, within about seven fragmented hours a week, a budget of a couple of subscriptions, and a preference for privacy. The user's three stated failures, interactivity, currency and tailoring, are direct symptoms. Integration, decay and sustaining effort are the deeper risks over a ten-year horizon. **[inference, grounded in stated answers]**

## 7. Constraints and boundaries that any direction must respect

| ID | Constraint | Basis |
|---|---|---|
| C1 | About an hour a day on average, varying a lot: short weekday slots around the commute, longer weekend blocks. | [stated] |
| C2 | Running costs of roughly a couple of subscriptions a month. No large hardware spend. | [stated] |
| C3 | Preference that the detailed model of the user is not held by a cloud AI provider. **This is in tension with C2**, because capable, affordable AI is mostly cloud-hosted today. The tension is carried to alternatives (WI-013). | [stated]; tension [inference] |
| C4 | Learning is private by default. Sharing is a case-by-case choice. | [stated] |
| C5 | The user keeps the reasoning, understanding and judgement (B1). The AI may direct sequencing (D-001). | [stated], D-001 |
| C6 | Capability is the goal. Real projects are means and evidence (D-003). The business is what capability is *for*, not something the system pursues. | D-003; [stated] purpose |
| C7 | The user learns while building the system, but its construction is not run as one of its own learning projects (D-002). | D-002 |

## 8. Working assumptions and open diagnostic questions

| ID | Proposition | Status |
|---|---|---|
| A-003 | Useful capability is judged by real-world application and demonstrable output, not credentials. **Challenge:** the 10-year aim ("respected", "influential") also depends on reputation, which may partly require recognised signals. | Provisional; strengthened by the user's ability-framed targets |
| A-005 | Weekday commute slots suit short, low-setup activity (practice, retrieval, reading, reflection) more than build work, which falls mainly at weekends. | Provisional, [inference] from C1 |
| A-006 | The day job is a real learning venue, but the AI tools available there are extremely limited, so it cannot be the main place for AI-assisted learning. It remains a major source of real-world performance and judgement. | Validated by the user's statement, 2026-09-25 (WI-011) |
| A-007 | The 10-year advisory aim and the business aim are the same path: the business is policy advice. | Validated by the user's statement, 2026-09-25 (WI-012) |

Resolved by the user: WI-011 (the day job is a learning venue, but its AI tools are extremely limited) and WI-012 (the policy advice is the business). Carried forward: WI-013 (privacy versus cost) and WI-006 (meta-work and permanence, assessed in M9 and M10, due for the pre-Gate-5 challenge).

## 9. What successful change would look like (problem-level, not a design)

Over time, and judged by demonstration rather than completion **[stated targets; A-003]**:

- **1 year:** the user runs agentic workflows they built and understands them. They can use refreshed econometrics on real questions, and can reason about software quality.
- **3 years:** they build and *validate* AI-assisted economic analysis and can defend its robustness to academic economists and senior officials. They have begun to sell insight.
- **Throughout:** their own reasoning demonstrably improves, not just their output (B1, M8). Capabilities stay current as fields move (M3, AM-4) and do not decay (M7, AM-10). Effort is sustained on about seven hours a week (M9, M10).
