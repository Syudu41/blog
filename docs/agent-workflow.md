# What the Manim agent currently does

TensorQuill currently has a local rendering CLI and a documented coding-agent workflow. It does not have an independent background agent that reads a request, writes scenes, watches renders, fixes them and publishes without a host coding-agent session.

The coding agent in the session currently plans and writes scenes, invokes the CLI, inspects outputs, runs independent checks, records review evidence, and publishes approved media. `python -m tensorquill new` only creates a scaffold; `render` runs an existing scene and checks media integrity. Neither command calls a language model or evaluates explanatory quality.

## Resume from files, not chat memory

A fresh coding-agent session should read:

1. `AGENTS.md` and `docs/visual-standards.md`.
2. The selected task's `requirements.md`, `task.json`, `scene.py`, and `content.md`.
3. Existing output, `review.json`, task-specific checks and evidence.
4. Recent `runs/` logs and reports if they are present locally.
5. The corresponding authored page in `website/samples/`.

Continue from that evidence. A scaffold or successful renderer exit is not a completed animation. Never infer that a review passed from a chat summary, and never claim a background process is running when none was started.

Task files and committed evidence survive context-window resets. Local `runs/` directories are ignored by Git; important verification results and review evidence must be stored in the task folder before committing. Do not rerender an unchanged scene merely because the chat context was lost.

A self-running scene-authoring agent would require a separate host and execution loop. That component is not implemented; no model API is configured by this project.
