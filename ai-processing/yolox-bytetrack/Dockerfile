FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# 環境変数設定
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Tokyo
ENV PYTHONPATH=/workspace:/workspace/YOLOX:/workspace/ByteTrack

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

# 動画処理関連パッケージ
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    && rm -rf /var/lib/apt/lists/*

# Python環境設定
RUN python3 -m pip install --upgrade pip setuptools wheel

# 作業ディレクトリ設定
WORKDIR /workspace

# 基本的なPython依存関係をインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# YOLOX公式リポジトリのクローンとインストール
RUN git clone https://github.com/Megvii-BaseDetection/YOLOX.git /workspace/YOLOX
RUN cd /workspace/YOLOX && \
    pip3 install -e .

# ByteTrack公式リポジトリのクローンとインストール
RUN git clone https://github.com/ifzhang/ByteTrack.git /workspace/ByteTrack
RUN cd /workspace/ByteTrack && \
    pip3 install -r requirements.txt && \
    python3 setup.py develop

# アプリケーションファイルをコピー
COPY src/ /workspace/src/
COPY config.yml /workspace/
COPY configs/ /workspace/configs/

# 必要なディレクトリを作成
RUN mkdir -p /workspace/models \
    /workspace/data \
    /workspace/output/videos \
    /workspace/output/tracking_data \
    /workspace/output/frames \
    /workspace/output/logs

# 権限設定
RUN chmod +x /workspace/src/*.py

# デフォルトのYOLOXモデルをダウンロード（オプション）
RUN cd /workspace/models && \
    wget -q https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth || \
    echo "モデルファイルのダウンロードに失敗しました。手動でダウンロードしてください。"

# GPU環境の設定
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# エントリーポイント設定
WORKDIR /workspace
CMD ["/bin/bash"]