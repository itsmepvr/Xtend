# Build on Ubuntu 18.04 so we get glibc 2.27
FROM --platform=linux/amd64 ubuntu:18.04

ARG APP_VERSION

# 1️⃣ System deps: Ruby for FPM, UPX, build tools
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
      libbz2-dev \
      ca-certificates \
      upx \
      ruby-full \
    && rm -rf /var/lib/apt/lists/*

# 2️⃣ FPM lives in a gem
RUN gem install --no-document fpm

# 3️⃣ Build & install Python 3.11
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz && \
    tar xf Python-3.11.9.tgz && \
    cd Python-3.11.9 && \
    ./configure --enable-optimizations && \
    make -j"$(nproc)" && \
    make altinstall && \
    rm -rf /tmp/Python-3.11.9*

# 4️⃣ Symlink python3 → 3.11, pip3 → pip3.11
RUN ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3 && \
    ln -sf /usr/local/bin/pip3.11   /usr/local/bin/pip3

WORKDIR /app
COPY . .

# 5️⃣ Install Python deps + PyInstaller
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt pyinstaller

# 6️⃣ Build the one-file executable & UPX-compress it
RUN pyinstaller --clean --onefile --name xtend src/xtend/cli.py && \
    upx --best dist/xtend

# 7️⃣ .deb via FPM
RUN mkdir -p pkg/usr/local/bin && \
    cp dist/xtend pkg/usr/local/bin/ && \
    fpm -s dir -t deb \
        -n xtend \
        -v "${APP_VERSION#v}" \
        --deb-compression=xz \
        -C pkg \
        --description "Xtend Screen Management Tool"

# 8️⃣ Prepare AppDir for AppImage
RUN mkdir -p AppDir/usr/bin \
             AppDir/usr/share/applications \
             AppDir/usr/share/icons/hicolor/256x256/apps && \
    cp dist/xtend AppDir/usr/bin/ && \
    cp src/xtend/resources/xtend.desktop AppDir/usr/share/applications/ && \
    cp src/xtend/resources/xtend.png AppDir/usr/share/icons/hicolor/256x256/apps/xtend.png

# 9️⃣ Download AppImageKit’s appimagetool & build
RUN wget -qO appimagetool.AppImage \
      https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage && \
    chmod +x appimagetool.AppImage && \
    ./appimagetool.AppImage AppDir dist/xtend.AppImage

# ⏩ Copy everything back to the Actions workspace
CMD cp dist/* /github/workspace/dist/
