# Alternative set: Permanent Learning System

Iteration 1 · produced by `generate-alternatives` · 2026-09-26

Inputs: problem model `art-problem-model` (mechanisms M1 to M10, constraints C1 to C7, the two-halves observation), intent model `art-intent-model` (boundaries B1 to B6), ambition map `art-ambition-map` (carried AM-3, AM-4, AM-5, AM-10), decisions D-001 to D-003, assumptions A-003 to A-007, open items WI-006, WI-013 and WI-014. Current evaluations G1-E1, G2-E1 and G3-E1.

Labels: **[stated]**, **[inference]**, **[general knowledge]** and **[assumption]** as in the problem model. Directions are described at vision level: mechanism, intended change, people, assumptions and boundaries. They are not ranked here; the comparison is in `direction-comparison.md`. Nothing below is a feature, interface or technical design.

## 1. Settled points every direction inherits

These are not open, so no direction varies them:

- **The AI leads sequencing** (D-001). Every direction has the AI choosing what comes next toward the user's target capabilities; they differ in *what the learning mostly consists of* and *where evidence comes from*.
- **Capability is the goal** (D-003); projects and consequential activity are means and evidence.
- **The user does the thinking** (B1, C5); M8 is a test every direction must pass.
- **Private by default** (C4), about seven fragmented hours a week (C1), about two subscriptions (C2).
- **The user learns while building, but the build is not run as one of the system's own projects** (D-002, C7).

## 2. Dimensions along which directions genuinely differ

| Dimension | Range explored | Why it matters here |
|---|---|---|
| **Primary learning mechanism** | designed tutoring sessions · real integrating projects · human judgement and dialogue · existing courses and tools | M1, M5 and the integration problem in problem-model section 3 |
| **Primary venue for consequential practice** | personal time only · day job plus personal time · outside people and forums | the two-halves observation; A-006 |
| **Source of evidence about capability** | AI assessment · project outputs · human judges | B4, A-003 (reputation), M8 |
| **Where the detailed learner model lives** (WI-013) | held by an AI or learning provider · held by the user, shown to a cloud AI per session · held and processed entirely locally | C2 versus C3, AM-3 |
| **Build extent** | assemble existing products · light build on commodity AI · substantial custom build | M10, D-002, WI-006 |
| **Cadence** | continuous daily system · cyclical programmes with reviews · event-driven by projects | M6, M9 |

The first two dimensions define the directions below. The learner-model location, build extent and cadence are **cross-cutting axes**: most directions can take several positions on them, so they are set out separately in section 4 rather than multiplied into cosmetic variants.

## 3. Directions

### Direction A — AI tutor on a user-owned record

**Core mechanism.** The user keeps a durable, portable record of target capabilities, current mastery, evidence and artefacts (AM-3). Each session, a general-purpose AI reads the relevant part of that record and acts as tutor, curriculum manager and examiner: it designs short practice, retrieval and challenge sessions, assesses the answers, updates the record and decides the next step. Over time sessions shift from exercises toward projects (B4).

**Intended change.** Directly repairs the user's three stated failures: interactive (M1), current (M3) and tailored (M2), with sequencing (M4) and maintenance (M7, AM-10) driven by the record.

**People.** The user alone; others appear only when the user chooses to bring evidence in.

**Critical assumptions.** A-008: an AI given a well-kept external record can tutor and assess well enough across sessions. The AI's assessment is a reliable enough signal of real capability. Short commute slots suit AI-led practice (A-005).

**Distinguishing boundaries.** Closest to the seed. Evidence is mostly AI-generated. Integration across domains happens only if the AI designs it in.

### Direction B — Project spine (learning through one integrating body of work)

**Core mechanism.** Learning is organised around a continuing sequence of real, private projects at the user's intersection, for example building and validating AI-assisted analysis of public policy questions with public data. The AI chooses the next project and the next gap to close (D-001), acts as reviewer and examiner, and pulls in foundations such as theory, econometrics and software practice *when the project exposes the need*. The project outputs are the capability evidence and the durable body of work (B6).

**Intended change.** Attacks integration (problem-model section 3) and separation from real use (M5) head-on. The AI-systems half gets a venue it lacks at work. Demonstrable artefacts accumulate from the start.

**People.** The user; the artefacts can later be shown selectively to officials, academics or future clients (C4).

**Critical assumptions.** Just-in-time foundations are enough for methodological depth ("validate", "robust"). Projects of a useful size fit into about seven fragmented hours, mostly at weekends (A-005). The AI reviewer does not quietly do the building (M8).

**Distinguishing boundaries.** Learning is project-first, not session-first. Foundations are pulled, not pushed. Risk of gaps in areas no project touches.

### Direction C — Assembled stack of existing products, minimal build

**Core mechanism.** Use existing products as they are: an AI assistant subscription, commercial courses or AI tutors for specific subjects, a spaced-repetition tool, and a notes tool. A simple written plan and a monthly or quarterly review with the AI set priorities. There is no custom learner model beyond what each product keeps.

**Intended change.** Better than today's unstructured learning at the lowest meta-work (M10). Effort goes almost entirely to learning.

**People.** The user; product vendors hold most of the data.

**Critical assumptions.** Existing products are good enough in each domain, and a periodic review can do the cross-domain integration that none of them does. This rests on WI-014: current tools have not been researched.

**Distinguishing boundaries.** Minimal build, which reduces the "learn while building" value of D-002. The learner model is fragmented and mostly held by providers, against C3 and AM-3.

### Direction D — Human-anchored learning, AI as preparer

**Core mechanism.** Capability is built around recurring *human* judgement: a mentor or two, a sparring partner in academic economics, a small reading or seminar group, and presenting or defending work privately to people whose opinion counts (AM-5). The AI's role is to prepare the user for each encounter, drill, rehearse and critique, and to debrief afterwards and choose the next focus.

**Intended change.** Evidence of capability comes from credible people, which addresses A-003's reputation challenge and the three-year target of conversing with academics and senior officials. Human feedback is hard for AI to fake, which protects B1 (M8). Commitments to other people sustain effort (M9).

**People.** Brings in mentors, peers and academics as sources of challenge, not as users (AM-5). Needs their willingness (A-009).

**Critical assumptions.** Suitable people are available and willing at a cost within C2. Private-by-default can hold while working with a small trusted circle (C4).

**Distinguishing boundaries.** Depends on others' time and availability. Weak on the AI-systems half unless peers in that field are found. Cadence set by meetings, not by the learner model.

### Direction E — Two venues: day job for economics and advice, personal time for AI systems

**Core mechanism.** Split deliberately by the two-halves observation. Economics refresh and advisory judgement are developed *through the day job*, with the AI helping the user plan deliberate practice at work and reflect on it afterwards outside work (A-006: the AI tools at work are extremely limited, so the AI works on the user's reflections, not on work material). Personal hours go almost entirely to the AI-systems half. Integration is attempted later, once both halves are stronger.

**Intended change.** Uses the richest consequential venue the user has (M5) and frees the scarce personal hours (M6, M10) for the half with no other outlet.

**People.** The user, the user's team and government clients as the context of practice; confidentiality limits stay with the employer's rules.

**Critical assumptions.** Work gives enough stretch in theory and econometrics, not only applied practice. Reflection outside work is useful without work material, within confidentiality.

**Distinguishing boundaries.** Integration is deferred rather than built from the start. The system reaches into working life, so it depends on the role continuing.

## 4. Cross-cutting axes

### Where the learner model lives (WI-013)

| Position | What it means | Fit with C2 and C3 |
|---|---|---|
| **P1 Provider-held** | Each product or AI provider keeps its own picture of the user. | Cheapest; conflicts with C3 and AM-3. Natural for C. |
| **P2 User-held record, cloud AI per session** | The durable record stays in files the user controls; the parts needed for a session are shown to a cloud AI and not otherwise kept by it (subject to the provider's terms). | Within C2. Meets C3 for the *durable* model, but session content is still seen by the provider. Natural for A, B, D and E. |
| **P3 Fully local** | Record and AI both run on the user's own hardware. | Fully meets C3; today capable local AI generally needs hardware beyond C2 **[general knowledge, not researched]**, and would weaken tutoring quality on modest hardware. |

**Inference.** P2 is the only position that is compatible with both C2 and the core of C3, but it asks the user to accept that the *contents of sessions* pass through a cloud provider. That is a trade-off only the user can accept (WI-013), to be put at convergence.

### Build extent (D-002, M10, WI-006)

Assembling (C) minimises meta-work but gives little building to learn from. A light build on commodity AI (natural for A, B, E) turns some meta-work into the one-year target of running agentic workflows (D-002). A substantial custom build maximises that learning but is where upkeep and tinkering can starve economics (M10). Any direction except C can sit at "light".

### Cadence (M6, M9)

A continuous daily system suits commute slots (A-005). Cyclical programmes, for example quarter-long focused pushes with a review, suit weekend project work and give natural points to reassess (AM-4). Event-driven cadence is natural for D. These combine; cadence does not by itself define a direction.

## 5. Regions considered and not developed

| Region | Why not developed as a direction |
|---|---|
| Formal study anchor (a part-time degree or accredited programme with AI support) | Conflicts with C2 (cost) and C1 (fixed load), and weights credentials over capability (B2). Its one strength, recognised signals for the 10-year aim (A-003), is carried as a criterion instead, and Direction D covers credibility with people. |
| Learning in public as the engine (audience feedback, publishing) | Ruled out as a default by the user (C4, WI-010). Case-by-case sharing remains available within any direction. |
| Productised or multi-learner system | Deferred by the user's scope (WI-009, A-002). |
| Real-world results as the organising goal | Rejected by the user (D-003). B uses projects only as means and evidence. |
| AI does the work, the user supervises | Violates B1 and C5. |

## 6. Alternative-related assumptions proposed

- **A-008.** A general-purpose cloud AI, given a well-kept user-held record at the start of each session, can tutor, assess and sequence well enough across months to act as the curriculum manager in Directions A, B and E. *Provisional, [inference]; test cheaply early.*
- **A-009.** A small number of credible people (mentors, academic or official sparring partners) are available and willing to give private challenge at a cost within C2. *Provisional, [assumption]; affects Direction D most and AM-5 in every direction.*

The comparison of these directions, and the agent's recommendation, is in `direction-comparison.md`.
