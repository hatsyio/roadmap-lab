# AGENTS.md

Instructions for LLM agents that use or change this repo.

## Using the repo as reference code

- `roadmap.toml` is the index. Each `evidenced` node lists the paths that demonstrate it.
  Start there to find the folder for a topic.
- Each folder under `skeletons/` and `examples/` is self-contained. Read its `README.md`
  first: it states what the folder shows, how to run it, and what to adapt when you copy it.
- When you copy code into another project, copy the patterns and the pinned tool versions,
  then re-check the versions: this repo can lag behind by up to the Dependabot cooldown.
- Only `skeletons/` and `examples/` are reference code. `scripts/` and the root tooling
  maintain this repo and are not meant to be copied.

## Changing the repo

- Run `make ci` before you claim a change is done. It is the same command CI runs.
- After you edit `roadmap.toml`, run `make readme`. `make ci` fails if the README table is stale.
- Mark a node `evidenced` only when a path in this repo proves it. Add the path to `evidence`.
- A new folder under `skeletons/` or `examples/` must have:
  - its own manifest and lockfile (no shared dependencies with the root),
  - a `Makefile` with a `ci` target that runs lint, format check, typecheck and tests,
  - a `README.md` with three sections: **What it shows**, **Run it**, **Adapt it**,
  - a `.env.example` when it reads env vars.
- Pin every version (packages, base images, actions major tags). No `latest`.
- Do not copy text from roadmap.sh. Use the node slug, a hand-written title and the link.

## Documentation exception

Freeform docs live in the root `README.md`. The only exception is the per-folder
`README.md` under `skeletons/` and `examples/`: it is the context an LLM needs to reuse
that folder, so each folder keeps its own.

## Workflow

- Tracker: GitHub Issues on `hatsyio/roadmap-lab`. Every change references an issue.
- Branches: `<type>/<issue>/<short-name>`. Base branch: `main`.
- Commits: Conventional Commits, with `Refs: #<issue>` in the footer.
