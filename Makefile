NUM_OF_PARENT:=$(shell echo $$(( $(words $(MAKEFILE_LIST)))) )
topdir:=$(realpath $(dir $(word $(NUM_OF_PARENT),$(MAKEFILE_LIST))))

MARKDOWNLINT := davidanson/markdownlint-cli2-rules:v0.12.1
PYTHON := python:3.12-slim

all: help

render:
	$(MAKE) -C api/ $@

mock-server-up:
	$(MAKE) -C api/ $@

mock-server-down:
	$(MAKE) -C api/ $@

lint-markdown:
	docker run --rm -v $(topdir):/workdir $(MARKDOWNLINT)

lint-apispec:
	$(MAKE) -C api/ lint-apispec

# The specification checks: JSON format, references, the meta-schema, the entity schemas and
# examples, the role vocabulary, product neutrality and the docs index (tools/validate.py).
validate:
	docker run --rm -v $(topdir):/repo -w /repo $(PYTHON) sh -c 'pip install -q -r tools/requirements.txt && python3 tools/validate.py'

lint: lint-markdown lint-apispec validate

conform-json:
	docker run --rm --user $$(id -u):$$(id -g) -v $(topdir):/repo -w /repo $(PYTHON) python3 -c 'import json,pathlib; [p.write_text(json.dumps(json.loads(p.read_text()), indent=4, ensure_ascii=False) + "\n") for p in pathlib.Path(".").rglob("*.json") if not any(x.startswith(".") for x in p.parts)]'

help:
	@echo "teds"
	@echo "make lint           - Lint Markdown, the API specification, and run the specification checks"
	@echo "make render         - Bundle the specification for api/docs/index.html"
	@echo "make mock-server-up - Start a mock API server on http://localhost:4010"
	@echo "make conform-json   - Rewrite every JSON file in the 4-space format the checks expect"

.PHONY: all render mock-server-up mock-server-down lint-markdown lint-apispec validate lint conform-json help
