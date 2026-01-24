FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# 環境変数設定
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Tokyo

# システムパッケージのインストール + deadsnakes PPAでPython 3.12
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    build-essential \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python 3.12をデフォルトに設定
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# pip を Python 3.12 用にインストール
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# pipのアップグレード
RUN python3 -m pip install --upgrade pip setuptools wheel

# 作業ディレクトリ設定
WORKDIR /workspace

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# モデルダウンロードスクリプトをコピー
COPY download_model.py .

# テストスクリプトをコピー
COPY test_environment.py .

# デフォルトコマンド
CMD ["/bin/bash"]
