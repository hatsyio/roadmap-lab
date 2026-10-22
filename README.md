# roadmap-lab

Small, focused, runnable reference projects, plus a curated [roadmap.sh](https://roadmap.sh)
checklist where every check links to code.

The repo has two uses:

- **Reference for an LLM.** To start a new project, point an LLM at the folders you want
  to reuse, for example `skeletons/python-api` or `examples/<topic>`.
- **Evidence of skills.** A roadmap.sh node counts as done only when a folder in this repo
  proves it.

## Layout

| Path | Content |
| --- | --- |
| `skeletons/` | Complete project baselines: app, Docker, compose, CI, `make ci`. |
| `examples/` | Small projects, one topic each. |
| `roadmap.toml` | The checklist and the index of the repo: roadmap.sh node -> evidence paths. |
| `scripts/roadmap.py` | Validates `roadmap.toml` and renders the table below. |
| `AGENTS.md` | Instructions for LLM agents that read or change this repo. |

Every folder under `skeletons/` and `examples/` is self-contained: it has its own manifest,
lockfile, `Makefile` with `make ci`, and a short `README.md`. You can copy a folder as it is.

## Development

Requirements: [uv](https://docs.astral.sh/uv/) and `make`.

```bash
make ci       # lint + typecheck + tests + checklist check (same as GitHub Actions)
make readme   # re-render the checklist table after you edit roadmap.toml
```

Install the git hooks once:

```bash
uv run pre-commit install
```

Dependencies stay current through Dependabot (`.github/dependabot.yml`), with a 14-day
cooldown before a new release is proposed.

## Contributing

- Tracker: GitHub Issues. Every change references an issue.
- Branches: `<type>/<issue>/<short-name>`, for example `feat/2/python-api`.
- Commits: [Conventional Commits](https://www.conventionalcommits.org/).

## Roadmap checklist

Generated from `roadmap.toml` by `make readme`. Do not edit the table by hand.

<!-- roadmap:start -->
Evidenced: **0 / 12**

| Roadmap | Node | Status | Evidence |
| --- | --- | --- | --- |
| [python](https://roadmap.sh/python) | FastAPI (`fast-api`) | pending | - |
| [python](https://roadmap.sh/python) | Pydantic (`pydantic`) | pending | - |
| [python](https://roadmap.sh/python) | uv (`uv`) | pending | - |
| [python](https://roadmap.sh/python) | pytest (`pytest`) | pending | - |
| [docker](https://roadmap.sh/docker) | Dockerfiles (`dockerfiles`) | pending | - |
| [docker](https://roadmap.sh/docker) | Docker Compose (`docker-compose`) | pending | - |
| [devops](https://roadmap.sh/devops) | GitHub Actions (`github-actions`) | pending | - |
| [sql](https://roadmap.sh/sql) | Window functions (`window-functions`) | pending | - |
| [postgresql-dba](https://roadmap.sh/postgresql-dba) | GiST indexes (`gist`) | pending | - |
| [postgresql-dba](https://roadmap.sh/postgresql-dba) | EXPLAIN (`explain`) | pending | - |
| [data-engineer](https://roadmap.sh/data-engineer) | dbt (`dbt`) | pending | - |
| [data-engineer](https://roadmap.sh/data-engineer) | BigQuery (`google-bigquery`) | pending | - |
<!-- roadmap:end -->

## License

Code: [MIT](LICENSE). Roadmap names and links belong to [roadmap.sh](https://roadmap.sh);
this repo links to them and does not copy their content.
