FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# 環境変数設定
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Tokyo

# システムパッケージのアップデートと必要パッケージのインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    unzip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgoogle-glog-dev \
    libgflags-dev \
    libprotobuf-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# TensorRTのインストール（バージョン不整合を避けるため段階的に）
RUN apt-get update && apt-get install -y \
    libnvinfer8 \
    libnvinfer-plugin8 \
    && rm -rf /var/lib/apt/lists/*

# TensorRT開発パッケージのインストール
# システムレベルのTensorRTはランタイムのみインストール
# 開発機能はPythonバインディングで提供されるため、
# システムパッケージの依存関係エラーは回避する
RUN apt-get update && \
    echo "TensorRTランタイムライブラリは既にインストール済み" && \
    echo "開発機能はpip install tensorrtで提供されます" && \
    rm -rf /var/lib/apt/lists/*

# TensorRTの追加設定
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Python環境設定
RUN python3 -m pip install --upgrade pip setuptools wheel

# 作業ディレクトリ設定
WORKDIR /workspace

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# OpenCVのビデオコーデック追加インストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    && rm -rf /var/lib/apt/lists/*

# Jupyter環境設定（オプション）
RUN pip3 install jupyter jupyterlab
EXPOSE 8888

# サンプルスクリプト用ディレクトリ
RUN mkdir -p /workspace/samples

# エントリーポイント設定
CMD ["/bin/bash"]