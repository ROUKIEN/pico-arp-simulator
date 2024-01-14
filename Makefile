APP_DIR=./AppDir

BIN_APPIMAGE_BUILDER=./tools/appimage-builder-1.1.0-x86_64.AppImage

build: $(BIN_APPIMAGE_BUILDER)
	$(BIN_APPIMAGE_BUILDER) --skip-tests

clean:
	@rm -rf build_Linux

setup: $(BIN_APPIMAGE_BUILDER)

$(BIN_APPIMAGE_BUILDER):
	mkdir -p tools
	wget -O $@ https://github.com/AppImageCrafters/appimage-builder/releases/download/v1.1.0/appimage-builder-1.1.0-x86_64.AppImage
	chmod +x $@
	$@ --version
