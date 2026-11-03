# Commit conventions

- Commit every README update when it is complete.
- Commit each completed feature or subfeature separately. Keep unrelated changes out of the same commit so the history is easy to track.
- Write clear, concise commit messages in one or two sentences describing the change.
- Use a bulleted commit body only when a whole feature or subfeature needs additional explanation.
- Run checks appropriate to the change before committing. Stage only files belonging to that change; preserve unrelated user edits.

# Manim output and website workflow

- Keep each render task in `tasks/<task-id>/`, including requirements, editable Manim source, generated output, website explanation, and review evidence.
- Inspect every generated output and compare it against every task requirement. Run relevant numerical, media, typography, and layout checks; record actual evidence, not assumed passes.
- Publish output to `website/` only after all checks and requirements pass. Use `scripts/visualization_workflow.py` to prepare the review, publish approved artifacts, and check their integrity. See `docs/visualization-workflow.md` for the process.
- Re-review output after any requirement, source, explanation, or artifact changes. Do not bypass a failed check or relabel a Manim output as a concept preview.
- Build the whole website with Sphinx, MyST Markdown, and Furo; retain the white background and Arial-family text. All mathematics uses LaTeX.
- For explanatory tasks, storyboard and review the visual progression using `docs/visual-standards.md`. Passing rendering and media checks alone does not establish explanatory quality.
