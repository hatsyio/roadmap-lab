# Local == CI: GitHub Actions runs `make ci` and nothing else.
UV_RUN := uv run --frozen
export PYTHONPATH := scripts

.PHONY: ci lint typecheck test roadmap readme

ci: lint typecheck test roadmap

lint:
	$(UV_RUN) pre-commit run --all-files --show-diff-on-failure

typecheck:
	$(UV_RUN) mypy

test:
	$(UV_RUN) python -m unittest discover -s tests -v

roadmap:
	$(UV_RUN) python scripts/roadmap.py check

readme:
	$(UV_RUN) python scripts/roadmap.py render
