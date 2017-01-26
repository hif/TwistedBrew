ROOT_DIR := $(shell pwd)
X86_TWISTED_IMAGE_TAG := twistedbrew/twistedbrew
ARM_TWISTED_IMAGE_TAG := twistedbrew/twistedbrew:arm
ARM_PYTHON_IMAGE_TAG := twistedbrew/python:arm

docker-build:
	docker build -t ${X86_TWISTED_IMAGE_TAG} -f docker/x86/twistedbrew/Dockerfile .

docker-arm-build-python:
	docker build -t ${ARM_PYTHON_IMAGE_TAG} -f docker/arm/python/Dockerfile .

docker-arm-build: docker-arm-build-python
	docker build -t ${ARM_TWISTED_IMAGE_TAG} -f docker/arm/twistedbrew/Dockerfile .