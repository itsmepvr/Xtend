# Build on Ubuntu 18.04 for glibc 2.27 compatibility
FROM --platform=linux/amd64 ubuntu:18.04

ARG APP_VERSION

# 1) System deps: UPX, Ruby (for fpm), build tools
RUN apt-get update && \
    apt-get install -y \
      wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
      libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev \
      libbz2-dev ca-certificates upx ruby-full && \
    rm -rf /var/lib/apt/lists/*

# 2) fpm via gem
RUN gem install --no-document fpm

# 3) Compile & install Python 3.11
RUN cd /tmp && \
    wget https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz && \
    tar xf Python-3.11.9.tgz && \
    cd Python-3.11.9 && \
    ./configure --enable-optimizations && \
    make -j"$(nproc)" && \
    make altinstall && \
    rm -rf /tmp/Python-3.11.9*

# 4) Symlink python3 → 3.11, pip3 → pip3.11
RUN ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3 && \
    ln -sf /usr/local/bin/pip3.11   /usr/local/bin/pip3

WORKDIR /app
COPY . .

# 5) Install PyInstaller + your deps
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt pyinstaller

# 6) Build one-file and UPX-compress
RUN pyinstaller --clean --onefile --name xtend src/xtend/cli.py && \
    upx --best dist/xtend

# 7) .deb via fpm
RUN mkdir -p pkg/usr/local/bin && \
    cp dist/xtend pkg/usr/local/bin/ && \
    fpm -s dir -t deb \
        -n xtend \
        -v "${APP_VERSION#v}" \
        --deb-compression=xz \
        -C pkg \
        --description "Xtend Screen Management Tool"

# 8) AppImage prep & build
RUN mkdir -p AppDir/usr/bin \
             AppDir/usr/share/applications \
             AppDir/usr/share/icons/hicolor/256x256/apps && \
    cp dist/xtend AppDir/usr/bin/ && \
    cp src/xtend/resources/xtend.desktop AppDir/usr/share/applications/ && \
    cp src/xtend/resources/xtend.png AppDir/usr/share/icons/hicolor/256x256/apps/xtend.png && \
    wget -qO appimagetool.AppImage https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage && \
    chmod +x appimagetool.AppImage && \
    ./appimagetool.AppImage AppDir dist/xtend.AppImage

# 9) Export everything back to GitHub Actions
CMD cp dist/* /github/workspace/dist/
