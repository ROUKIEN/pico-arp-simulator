appimage: builder ## generates .AppImages for linux
	docker run --rm -w /app -u $(shell id -u):$(shell id -g) -v $(shell pwd):/app --cap-add SYS_ADMIN --privileged builder
	chmod a+x *.AppImage
.PHONY: appimage

builder:
	docker build  --build-arg="U_ID=$(shell id -u)" --build-arg="G_ID=$(shell id -g)" -t $@ .
.PHONY: builder

clean:
	@rm -rf build_Linux *.AppImage *.zsync AppDir appimage-build __pycache__

TAG?=1.2.5
tag: ## tag the repo
	yq e -i '.AppDir.app_info.app_version = "$(TAG)"' AppImageBuilder.yml
	git add AppImageBuilder.yml
	git commit -m "bump to version v$(TAG)"
	git tag v$(TAG) -m "v$(TAG)"
.PHONY: tag
