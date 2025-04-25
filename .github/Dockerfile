FROM --platform=linux/amd64 ubuntu:18.04

ARG APP_VERSION

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.11 \
    python3-pip \
    upx-ucl \
    build-essential \
    fpm \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN python3.11 -m pip install --upgrade pip && \
    pip install -r requirements.txt pyinstaller

RUN pyinstaller --onefile --name xtend src/xtend/cli.py \
    --add-data "src/xtend/static:static" \
    --add-data "src/xtend/templates:templates" \
    --upx-dir /usr/bin \
    --exclude-module PyQt5.QtWebEngine

RUN mkdir -p pkg/usr/local/bin && \
    cp dist/xtend pkg/usr/local/bin/ && \
    fpm -s dir -t deb -n xtend -v $APP_VERSION \
        --deb-compression=xz \
        -C pkg \
        --description "Xtend Screen Management Tool"

RUN wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    && chmod +x appimagetool-x86_64.AppImage \
    && ./appimagetool-x86_64.AppImage dist/xtend

CMD ["sh", "-c", "cp -r dist/* /github/workspace/dist/"]