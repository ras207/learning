# Ideation Agent

## Protected system files

The contents of `.agents/ideation/` define the reusable ideation system.

During a normal ideation run, the agent MUST NOT create, modify, rename, or delete any file beneath `.agents/ideation/`.

The agent may read files beneath `.agents/ideation/` as needed to execute the workflow.

Files beneath `.agents/ideation/` may be changed only when the user explicitly asks to modify the ideation system itself.

Generated project artifacts MUST be written beneath:

`projects/<project-slug>/ideation/`

The generated vision artifact MUST be written to:

`projects/<project-slug>/ideation/vision.md`
