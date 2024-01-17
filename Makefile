APP_DIR=./AppDir

appimage: builder
	docker run --rm -w /app -u $(shell id -u):$(shell id -g) -v $(shell pwd):/app --cap-add SYS_ADMIN --privileged builder
.PHONY: appimage

builder:
	docker build  --build-arg="U_ID=$(shell id -u)" --build-arg="G_ID=$(shell id -g)" -t $@ .
.PHONY: builder

clean:
	@rm -rf build_Linux
