FROM ubuntu:18.04

ARG APP_VERSION

RUN apt-get update && \
    apt-get install -y \
      build-essential zlib1g-dev libncurses5-dev \
      libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev \
      libreadline-dev libffi-dev wget upx ruby-dev && \
    gem install fpm

WORKDIR /app
COPY . .

RUN wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz && \
    tar xzf Python-3.11.9.tgz && \
    cd Python-3.11.9 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall

RUN python3.11 -m pip install pyinstaller -r requirements.txt

RUN pyinstaller --onefile --name xtend src/xtend/cli.py && \
    upx --best --lzma dist/xtend

RUN mkdir -p pkg/usr/bin && \
    cp dist/xtend pkg/usr/bin/ && \
    fpm -s dir -t deb -n xtend -v ${APP_VERSION#v} \
      --deb-compression xz -C pkg

RUN wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage && \
    chmod +x linuxdeploy*.AppImage && \
    ./linuxdeploy*.AppImage --appdir AppDir -e dist/xtend \
      -i src/xtend/resources/icon.png -d src/xtend/resources/xtend.desktop \
      --output appimage

CMD ["cp", "xtend_*.deb", "Xtend-*.AppImage", "/github/workspace/dist/"]