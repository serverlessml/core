# Dmitry Kisler © 2020-present
# www.dkisler.com <admin@dkisler.com>

SHELL=/bin/bash

rebuild: build push push-latest

.PHONY: build run push \
	run-gcp run-gcp-local \
	run-aws run-aws-local \
	lint coverage-bump license-check rm


REGISTRY := slessml
VER := `cat ./src/VERSION`
PLATFORM := gcp
PY_VER := 3.8
BG := -d --name=core-$(PLATFORM)
DEMO_SUFF := ""
SERVICE := core-$(PLATFORM)-py$(PY_VER)$(DEMO_SUFF)

build:
	@docker build \
		-t ${REGISTRY}/${SERVICE}:${VER} \
		--build-arg PY_VER=$(PY_VER) \
		--build-arg VER=$(VER) \
		-f ./Dockerfile.$(PLATFORM)$(DEMO_SUFF) .

push:
	@docker push ${REGISTRY}/${SERVICE}:${VER}

push-latest:
	@docker tag ${REGISTRY}/${SERVICE}:${VER} ${REGISTRY}/${SERVICE}:latest
	@docker push ${REGISTRY}/${SERVICE}:latest

run-gcp-local:
	@docker run $(BG) \
		-p 8080:8080 \
		-v ${PWD}/e2e_test:/tmp \
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
		-v ${PWD}/e2e_test:/tmp \
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
