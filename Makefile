# Make NEXP Backend

STAGE?=dev

install-python-tools:
	pip install --upgrade pip && pip install pipenv
.PHONY: install-python-tools

install-deploy-dependencies:
	npm i -g serverless@1.67.3 && npm install
.PHONY: install-deploy-dependencies

build:
	./build-layer
.PHONY: build

deploy:
	sls deploy -s $(STAGE)
.PHONY: deploy
