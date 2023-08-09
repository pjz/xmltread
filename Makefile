
# This Makefile assumes it's being run someplace with pip available

PROJ=$(shell grep ^name pyproject.toml | cut -d\" -f2)
VERSION=$(shell grep ^version pyproject.toml | cut -d\" -f2)

.PHONY: default
default::
	@echo "dev - set up the dev virtualenv"
	@echo "wheel|$(PROJ) - build the $(PROJ) python package"
	@echo "docs - build the docs into docs/_build"
	@echo "pylint - run a linter on the codebase"
	@echo "mypy - run a typechecker on the codebase"
	@echo "test = run all tests in dev machine python"
	@echo "clean - remove all build artifacts"
	@echo "git-release - tag a release and push it to github"
	@echo "pypi-release - push a release to pypi"
	@echo "docs-release - build the docs and release to github pages"

PYTEST_ARGS = $(PYTEST_EXTRA)

INST_REQS=requirements.txt
DEV_REQS=requirements-dev.txt
DEV_ENV=.make.dev-env-sync
PIP_TOOLS=$(VIRTUAL_ENV)/bin/pip-compile

PIP_VENDORED_FLAGS=$(if $(PIP_VENDORED_DIR),-f $(PIP_VENDORED_DIR),)

$(PIP_TOOLS):
	@if [ -z "$$VIRTUAL_ENV" ] ; then \
	    echo "You should be in a virtualenv or other isolated environment before running this."; \
		exit 1; \
	fi
	pip install pip-tools

$(DEV_REQS): pyproject.toml $(PIP_TOOLS)
	pip-compile -q --resolver=backtracking --extra=dev --output-file=$@ $<

$(INST_REQS): pyproject.toml $(PIP_TOOLS)
	pip-compile -q --resolver=backtracking  --output-file=$@ $<

$(DEV_ENV): $(DEV_REQS) $(INST_REQS) $(PIP_TOOLS)
	pip-sync $(DEV_REQS) $(INST_REQS)
	pip install -e .
	touch $(DEV_ENV)

.PHONY: dev
dev: $(DEV_ENV)

WHEEL=./dist/$(PROJ)-$(VERSION)-py3-none-any.whl

.PHONY: wheel
wheel: $(WHEEL)
$(WHEEL):
	python -m build

mypy pylint test coverage: export PYTHONWARNINGS=ignore,default:::$(PROJ)

CODECOV_OUTPUT=--cov-report term

pylint: $(DEV_ENV)
	pytest $(PROJ) \
		--pylint --pylint-rcfile=.pylintrc \
		--pylint-error-types=EF \
		-m pylint \
		--cache-clear

.coverage:
	@echo "You must run tests first!"
	exit 1

coverage-html.zip: .coverage
	coverage html -d htmlconv
	cd htmlconv && zip -r ../$@ .

coverage.xml: .coverage
	coverage xml

test: $(DEV_ENV)
	pytest tests $(PYTEST_ARGS) -l

testf: PYTEST_EXTRA=--log-cli-level=DEBUG -lx --ff
testf: test

.PHONY: mypy
mypy:
	mypy --non-interactive --install-types $(PROJ)
	#pytest --mypy -m mypy $(PROJ)
	mypy --check-untyped-defs $(PROJ)

.PHONY: coverage
coverage:
	pytest --cov=$(PROJ) $(CODECOV_OUTPUT) tests $(PYTEST_ARGS)


.PHONY: not-dirty
not-dirty:
	@if [ `git status --short | wc -l` != 0 ]; then\
	        echo "Uncommited code. Aborting." ;\
	        exit 1;\
	fi

#SIGN=--sign
SIGN=

.PHONY: git-release
git-release: $(WHEEL) not-dirty
	@if [ `git rev-parse --abbrev-ref HEAD` != main ]; then \
		echo "You can only do a release from the main branch.";\
		exit 1;\
	fi
	@if git tag | grep -q ^$(VERSION) ; then \
	        echo "Already released this version.";\
	        echo "Update the version number and try again.";\
	        exit 1;\
	fi
	git push &&\
	git tag $(SIGN) $(VERSION) -m "Release v$(VERSION)" &&\
	git push --tags &&\
	git checkout release &&\
	git merge $(VERSION) &&\
	git push && git checkout main
	@echo "Released! Note you're now on the 'main' branch."

.PHONY: pypi-release
pypi-release: $(WHEEL)
	twine upload dist/$(PROJ)-$(VERSION)*

.PHONY: docs
docs:
	$(MAKE) -C docs html

docs-release: docs
	@if [ `git rev-parse --abbrev-ref HEAD` != main ]; then \
		echo "You can only do a release from the main branch.";\
		exit 1;\
	fi
	@DOCTAR=docs-$(VERSION).tgz &&\
	cd docs/_build &&\
	tar czf ../../$$DOCTAR html &&\
	cd ../.. &&\
	git checkout gh-pages &&\
	rm -rf docs &&\
	tar xzf $$DOCTAR &&\
	rm $$DOCTAR &&\
	mv html docs &&\
	touch docs/.nojekyll &&\
	git add -A docs &&\
	git commit -m "release docs $(VERSION)" &&\
	git push && git checkout main
	@echo "Docs released!"



.PHONY: clean
clean:
	rm -rf build dist *.egg-info shippable *.whl $(DEV_ENV)
	find . -name __pycache__ | xargs rm -rf
	find . -name \*.pyc | xargs rm -f

-include Makefile.proj
