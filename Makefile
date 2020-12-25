# Dmitry Kisler © 2020-present
# www.dkisler.com <admin@dkisler.com>

SHELL=/bin/bash

rebuild: build push

.PHONY: build run push \
	run-gcp run-gcp-local \
	run-aws run-aws-local


REGISTRY := slessml
VER := `cat ./src/VERSION`
PLATFORM := gcp
PY_VER := 3.8
SERVICE := core-$(PLATFORM)-py$(PY_VER)
BG := -d --name=core-$(PLATFORM)

build:
	@docker build \
		-t ${REGISTRY}/${SERVICE}:${VER} \
		--build-arg PY_VER=$(PY_VER) \
		-f ./Dockerfile.$(PLATFORM) .

push:
	@docker push ${REGISTRY}/${SERVICE}:${VER}

run-gcp-local:
	@docker run $(BG) \
		-p 8080:8080 \
		-v /tmp:/tmp \
		-e ML_RUN_LOCALLY=Y \
		-t ${REGISTRY}/${SERVICE}:${VER}

run-gcp:
	@docker run $(BG) \
		-p 8080:8080 \
		-v ${HOME}/projects/secrets/infra/gcp/key-pubsub.json:/key.json \
		-v /tmp:/tmp \
		-e GOOGLE_APPLICATION_CREDENTIALS=/key.json \
		-e ML_RUN_LOCALLY=N \
		-t ${REGISTRY}/${SERVICE}:${VER}

run-aws-local:
	@docker run $(BG) \
		-p 8080:8080 \
		-v /tmp:/tmp \
		-e ML_RUN_LOCALLY=Y \
		--entrypoint python \
		-t ${REGISTRY}/${SERVICE}:${VER} \
		/main.py

run-aws:
	@docker run $(BG) \
		-p 8080:8080 \
		-v /tmp:/tmp \
		-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		-e ML_RUN_LOCALLY=N \
		-t ${REGISTRY}/${SERVICE}:${VER}

rm:
	@docker rm -f core-$(PLATFORM)

coverage-bump:
	@./tools/coverage_bump.py

license-check:
	@./tools/license_check.py

lint:
	@pre-commit run -a --hook-stage manual
