# Dmitry Kisler © 2020-present
# www.dkisler.com <admin@dkisler.com>

SHELL=/bin/bash

rebuild: build push

test-run: build run

.PHONY: build run push

REGISTRY := slessml
SERVICE := core
VER := `cat VERSION`
PROJECT_ID := kedro-01
TOPIC_PREFIX := trigger_
PLATFORM := gcp
BG := -d --name=core-$(PLATFORM)

test:

build:
	@docker build \
		-t ${REGISTRY}/${SERVICE}:${VER} \
		-f ./Dockerfile.$(PLATFORM) .

push:
	@docker push ${REGISTRY}/${SERVICE}:${VER}

run:
	@docker run $(BG) \
		-p 8080:8080 \
		-v ${HOME}/projects/secrets/infra/gcp/key-pubsub.json:/key.json \
		-e GOOGLE_APPLICATION_CREDENTIALS=/key.json \
		-e PROJECT_ID=${PROJECT_ID} \
		-e TOPIC_PREFIX=${TOPIC_PREFIX} \
		-t ${REGISTRY}/${SERVICE}:${VER}

rm:
	@docker rm -f core-gcp

coverage-bump:
	@./tools/coverage_bump.py

license-check:
	@./tools/license_check.py
