FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

ARG U_ID=1000
ARG G_ID=1000

WORKDIR /app

RUN apt update && apt install -y curl software-properties-common binutils coreutils desktop-file-utils fakeroot fuse libgdk-pixbuf2.0-dev patchelf squashfs-tools strace util-linux zsync wget git

RUN add-apt-repository ppa:deadsnakes/ppa && apt update

RUN apt install -y python3.11 python3-pip

# Install appimagetool AppImage (only for appimage-buidler < v1.0.3)
RUN wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O /usr/local/bin/appimagetool && chmod +x /usr/local/bin/appimagetool

RUN wget -q -O /usr/local/bin/appimage-builder https://github.com/AppImageCrafters/appimage-builder/releases/download/v1.1.0/appimage-builder-1.1.0-x86_64.AppImage && chmod +x /usr/local/bin/appimage-builder

RUN wget -q https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && python3.11 /tmp/get-pip.py

RUN groupadd -g ${G_ID} bob-builder && useradd bob-builder -u ${U_ID} -g ${G_ID} && chown -R bob-builder:bob-builder /app && chmod -R 755 /app

USER bob-builder

CMD ["appimage-builder"]
