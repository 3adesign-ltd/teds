NUM_OF_PARENT:=$(shell echo $$(( $(words $(MAKEFILE_LIST)))) )
topdir:=$(realpath $(dir $(word $(NUM_OF_PARENT),$(MAKEFILE_LIST))))

REDOCLY := redocly/cli:2.55.0
SPECTRAL := stoplight/spectral:6.15.0
PRISM := stoplight/prism:5.14.3

all: help

docs/TypedEntityDataStore_bundled.yaml: TypedEntityDataStore.yaml $(wildcard schemas/*.json) $(wildcard examples/*.json)
	docker run --rm --user $$(id -u):$$(id -g) -v $(topdir):/api -w /api $(REDOCLY) bundle TypedEntityDataStore.yaml -o docs/TypedEntityDataStore_bundled.yaml

bundle: docs/TypedEntityDataStore_bundled.yaml

render: bundle
	@echo "Open $(topdir)/docs/index.html"

# Spectral on the bundle (it cannot follow some split references, as TADS notes), plus Redocly
# on the split source. Both must pass.
lint-apispec: bundle
	docker run --rm -v $(topdir):/api -w /api $(SPECTRAL) lint --fail-severity=warn docs/TypedEntityDataStore_bundled.yaml
	docker run --rm -v $(topdir):/api -w /api $(REDOCLY) lint TypedEntityDataStore.yaml

mock-server-up:
	docker run --rm --init -d --name mock-teds -v $(topdir):/data:ro -p 4010:4010 $(PRISM) mock /data/TypedEntityDataStore.yaml -h 0.0.0.0

mock-server-down:
	docker stop mock-teds

help:
	@echo "make bundle          - Bundle the split specification into docs/TypedEntityDataStore_bundled.yaml"
	@echo "make render          - Bundle, for docs/index.html to render"
	@echo "make lint-apispec    - Lint the specification (Spectral on the bundle, Redocly on the source)"
	@echo "make mock-server-up  - Start a mock API server on http://localhost:4010"
	@echo "make mock-server-down"

.PHONY: all bundle render lint-apispec mock-server-up mock-server-down help
