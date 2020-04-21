# Make NEXP Backend

STAGE?=dev

build:
	./build-layer
.PHONY: build

deploy:
	sls deploy -s $(STAGE)
.PHONY: deploy
