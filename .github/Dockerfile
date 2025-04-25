FROM --platform=linux/amd64 ubuntu:18.04

ARG APP_VERSION

# Install build dependencies
RUN apt-get update && \
    apt-get install -y \
    wget \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    curl \
    libbz2-dev \
    upx-ucl \
    fpm \
    && rm -rf /var/lib/apt/lists/*

# Download and compile Python 3.11
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz && \
    tar -xf Python-3.11.9.tgz && \
    cd Python-3.11.9 && \
    ./configure --enable-optimizations && \
    make -j $(nproc) && \
    make altinstall && \
    ln -s /usr/local/bin/python3.11 /usr/local/bin/python3 && \
    ln -s /usr/local/bin/pip3.11 /usr/local/bin/pip3 && \
    rm -rf /tmp/Python-3.11*

WORKDIR /app
COPY . .

# Install Python requirements
RUN python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt pyinstaller

# Build executable
RUN pyinstaller --onefile --name xtend src/xtend/cli.py \
    --add-data "src/xtend/static:static" \
    --add-data "src/xtend/templates:templates" \
    --upx-dir /usr/bin \
    --exclude-module PyQt5.QtWebEngine

# Create DEB package
RUN mkdir -p pkg/usr/local/bin && \
    cp dist/xtend pkg/usr/local/bin/ && \
    fpm -s dir -t deb -n xtend -v $APP_VERSION \
        --deb-compression=xz \
        -C pkg \
        --description "Xtend Screen Management Tool"

# Create AppImage
RUN wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    && chmod +x appimagetool-x86_64.AppImage \
    && ./appimagetool-x86_64.AppImage dist/xtend

CMD ["sh", "-c", "cp -r dist/* /github/workspace/dist/"]