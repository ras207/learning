# Ideation Workflow

## Output location

Each ideation run operates on a specific project identified by `<project-slug>`.

The workflow MUST write the generated vision artifact to:

`projects/<project-slug>/ideation/vision.md`

Before writing the vision, the agent MUST read the vision contract at:

`.agents/ideation/contracts/VISION_CONTRACT.md`

The contract defines the structure and quality bar for the generated vision. It is not itself an output and MUST NOT be modified during a normal ideation run.

## Write boundary

During normal execution, all generated or mutable project artifacts MUST remain beneath:

`projects/<project-slug>/ideation/`

The workflow MUST NOT write to `.agents/ideation/` unless the user explicitly asks to modify the ideation system itself.

## Synthesis behavior

When the workflow reaches vision synthesis:

1. Read `.agents/ideation/contracts/VISION_CONTRACT.md`.
2. Read the current project ideation state and relevant accumulated reasoning.
3. Synthesize a project-specific vision that satisfies the contract.
4. Write or update only `projects/<project-slug>/ideation/vision.md`.
5. Do not modify the contract or any other file beneath `.agents/ideation/`.
