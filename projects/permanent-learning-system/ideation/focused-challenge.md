# Focused challenge: chosen direction before Gate 5

Iteration 1 · produced by `focused-challenge` · 2026-09-27

**Proposition under test.** The user's chosen direction (D-005 with D-004): learning mainly through real, private projects at the intersection of economics, AI and policy. The AI maintains a user-owned graph of capabilities with the evidence for each, and each session chooses which part to build, maintain or test. Evidence comes from AI assessment and self-assessment. The durable record stays with the user, and session content passes through a cloud AI (P2).

Inputs: `art-problem-model`, `art-alternatives`, `art-direction-comparison`, decisions D-001 to D-005, assumptions A-003 to A-010, open items WI-006, WI-009 and WI-014.

This challenge tests the direction; it does not reopen D-005. The user chose it after being told that it is weaker on credibility with other people and on protecting their own judgement. Findings are ranked by consequence. Labels are as in the problem model.

## 1. Strongest objections and failure modes

### F1 · The AI marks work it helped create, so the graph can drift toward flattering itself (high)

**Objection.** In a project-led direction the AI helps build the project, chooses what to test and judges the result. Output can improve while the user's own reasoning does not (M8), and the graph would still record growing capability. This is the most direct threat to B1 and to the value of the whole record. **[inference]**

**Failure mode.** After two years the graph shows strong "validate agentic economic analysis" capability. The user cannot defend a method choice without AI help, and discovers this in front of an academic or a senior official.

**Response within D-005.**
- **Separate assessing from helping (A-010).** The examiner is independent of the tutoring and building assistant, sees only the capability claim and the user's own work, and ideally is a different model.
- **Evidence must show unaided reasoning.** A capability counts as evidenced only when the user demonstrates the reasoning themselves, for example explaining, defending or adapting the work without assistance. AI-assisted output alone is not evidence of capability. **[agent proposal, consistent with B1 and D-005]**
- **Prefer evidence the world can check.** Where possible, capability evidence should be something reality scores, not only a model's opinion: code that runs and passes checks, a published result reproduced, an estimate that holds up on new data, a forecast scored against what happened. This is not evidence from other people, so it stays within D-005, and it is the strongest available correction to shared AI blind spots. **[agent proposal]**
- **Calibrate self-assessment.** Comparing the user's self-rating with the examiner's makes over- and under-confidence visible over time.

**Residual.** Models from different providers share much of their training, so they can be wrong in the same way, especially on contested or fast-moving policy questions. Carried as part of A-010. **Severity after response: moderate, non-blocking.**

### F2 · Without human judgement, "credible" and "respected" have no direct evidence (high, accepted)

**Objection.** The three-year target of conversing credibly with academic economists and senior officials, and the ten-year aim of being a respected advisor, are judged by people (A-003 challenge). The chosen evidence sources cannot observe them. **[inference]**

**Status.** This is the trade-off the user accepted in D-005 after it was put to them on 2026-09-27. It is not relitigated here.

**Mitigation compatible with D-005.** The day job already supplies human feedback on economics and advice. The user's own notes on how work went (a meeting, a piece of advice, a challenge from officials) can count as **self-reported evidence** in the graph, without other people becoming part of the system and without work material going to a cloud AI (A-006, C4). **[agent proposal, within self-assessment]**

**Consequence for the vision.** The vision must say plainly that the system evidences *capability*, not *reputation*; reputation remains the user's own business outside it. **Severity: consciously accepted trade-off; non-blocking.**

### F3 · Meta-work could consume the first year (medium)

**Objection.** A graph, an examiner separate from the tutor, projects and the system build all draw on about seven hours a week (M10, WI-006). Building the system counts as learning under D-002, but only the parts that build target capability; upkeep and tinkering do not. The AI-systems half could crowd out the economics refresh. **[inference]**

**Response.** D-005 already puts graph maintenance on the AI, not the user, which removes the largest recurring cost. Two principles follow: **learning time comes before system time**, meaning the system starts minimal and grows only when a limitation blocks learning; and **balance is visible**, meaning the graph shows when a target area (for example econometrics) is being neglected. **Severity after response: moderate, non-blocking; WI-006 remains for downstream design and early use.**

### F4 · Tutoring from a record may not work well enough (medium)

A-008 is untested: a cloud AI reading a user-held record each session may sequence and assess poorly. If it fails, the direction does not collapse. The record and projects remain, and assembled existing tools (Direction C) can substitute for weak parts. Test it cheaply and early. **Severity: non-blocking; critical assumption.**

### F5 · Fit with fragmented time (low)

Projects need longer blocks (A-005). The build/maintain/test choice fits the time pattern naturally: short commute slots suit maintain and test, and weekend blocks suit build. This finding supports the direction rather than weakening it. **Non-blocking.**

### F6 · Confidentiality boundary (low, must be explicit)

Under P2, session content goes to a cloud provider. Projects must therefore use public material. Work material stays out of the system unless the employer's rules allow it (A-006). This is a boundary, not a risk to the direction. **Non-blocking; goes into the vision's boundaries.**

## 2. Contradictions checked

| Check | Result |
|---|---|
| AI chooses what to work on (D-001) versus the user keeping the thinking (B1) | Consistent. Sequencing is AI-led and reasoning is the user's, which the unaided-reasoning evidence rule enforces. |
| Projects as the main vehicle versus capability as the goal (D-003) | Consistent. Projects are the means and the evidence, and their outputs are judged for capability, not for results. |
| Private by default (C4) versus artefacts that can be demonstrated (B6) | Consistent. Demonstrable does not mean published; sharing is case by case. |
| P2 (D-004) versus the confidentiality of work | Consistent once F6 is a stated boundary. |
| Permanent (B3, AM-3) versus dependence on AI providers | Consistent under P2. The record is the user's and portable, and providers are replaceable. |

No unresolved contradiction was found.

## 3. Comparative challenge

Is a credible alternative materially stronger? The agent's recommended hybrid, which added human calibration, is stronger on F2. The user declined it with that trade-off visible, so it is not a basis for reopening. Direction A-led is weaker on integration and artefacts. Direction C is weaker on ownership and cross-domain integration, and is a fallback if A-008 fails. **No alternative is materially stronger given the user's recorded preferences.**

## 4. Result

| Finding | Severity | Response | Blocking? |
|---|---|---|---|
| F1 AI marks work it helped create | High, moderate after response | A-010; unaided-reasoning evidence rule; world-checkable evidence; self-assessment calibration | No |
| F2 No human evidence of credibility | High, accepted in D-005 | Day-job self-reports; vision states it evidences capability, not reputation | No |
| F3 Meta-work | Medium | AI keeps the graph; learning before system time; neglect made visible | No |
| F4 Record-based tutoring untested | Medium | Early test; Direction C as fallback | No |
| F5 Fragmented time | Low | Build/maintain/test matched to slot length | No |
| F6 Confidentiality | Low | Public material only; stated boundary | No |

**Recommended response.** Proceed to Gate 5 and synthesis. Carry as guiding principles: unaided reasoning is the evidence, prefer world-checkable evidence, learning time before system time, the record is the user's, private by default. Carry A-008, A-010, A-005 and A-003 as critical assumptions. The user may reject any agent proposal above; that would be a material change to this assessment.
