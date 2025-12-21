PYTHONPATH=./src/
PYTHON=./venv/bin/python

REPO_NAME=starplot-constellations

VERSION=$(shell ./venv/bin/python -c 'from build import __version__; print(__version__)')
VERSION_CHECK=$(shell gh release list \
		-R steveberardi/$(REPO_NAME) \
		--limit 1000 \
		--json tagName \
		--jq '.[] | select(.tagName == "v$(VERSION)")' | wc -c)

# Development ------------------------------------------
install: venv/bin/activate

lint: venv/bin/activate
	@$(PYTHON) -m ruff check src/ $(ARGS)

format: venv/bin/activate
	@$(PYTHON) -m black . $(ARGS)

test: venv/bin/activate
	PYTHONPATH=./src/ $(PYTHON) -m pytest --cov=src/ --cov-report=term --cov-report=html src/

venv/bin/activate: requirements.txt
	python -m venv venv
	./venv/bin/pip install -r requirements.txt

shell: venv/bin/activate
	$(PYTHON)

clean:
	rm -rf __pycache__
	rm -rf venv
	rm -rf build

build: venv/bin/activate
	@mkdir -p build
	$(PYTHON) build.py

# Releases ------------------------------------------
release-check:
	@CHECK="$(VERSION_CHECK)";  \
	if [ $$CHECK -eq 0 ] ; then \
		echo "version check passed!"; \
	else \
		echo "version tag already exists"; \
		false; \
	fi

release: release-check
	gh release create \
		v$(VERSION) \
		build/constellations.$(VERSION).parquet \
		--title "v$(VERSION)" \
		-R steveberardi/starplot-constellations

version: venv/bin/activate
	@echo $(VERSION)


.PHONY: clean test release release-check build
