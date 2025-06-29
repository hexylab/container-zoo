FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# 環境変数設定
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Tokyo
ENV PYTHONPATH=/workspace:/workspace/YOLOX:/workspace/ByteTrack:/workspace/src

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

# PyTorchを最初にインストール（YOLOX setup.py が必要とするため）
RUN pip3 install --no-cache-dir torch>=2.0.0 torchvision>=0.15.0 torchaudio>=2.0.0

# YOLOX公式リポジトリのクローンとセットアップ
RUN git clone https://github.com/Megvii-BaseDetection/YOLOX.git /workspace/YOLOX

# YOLOXの依存関係を先にインストール（setup.pyを通さず）
RUN pip3 install --no-cache-dir \
    opencv-python \
    loguru \
    tqdm \
    thop \
    ninja \
    tabulate \
    psutil \
    tensorboard \
    pycocotools>=2.0.2 \
    onnx>=1.13.0 \
    onnx-simplifier==0.4.10

# YOLOXを展開モードで使用（インストールではなくパス追加）
RUN cd /workspace/YOLOX && \
    python3 -c "import torch; print(f'PyTorch {torch.__version__} 確認完了')" && \
    echo "YOLOX: パスベース使用" && \
    ls -la

# 残りのPython依存関係をインストール
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# ByteTrack公式リポジトリのクローンとセットアップ
RUN git clone https://github.com/ifzhang/ByteTrack.git /workspace/ByteTrack

# ByteTrackの依存関係を修正してインストール
RUN cd /workspace/ByteTrack && \
    pip3 install --no-cache-dir lap && \
    mv yolox bytetrack_yolox && \
    mkdir -p bytetrack_yolox/tracker && \
    echo "# ByteTrack yolox package" > bytetrack_yolox/__init__.py && \
    echo "# ByteTrack tracker package" > bytetrack_yolox/tracker/__init__.py && \
    mkdir -p bytetrack_yolox/tracking_utils && \
    echo "# ByteTrack tracking_utils package" > bytetrack_yolox/tracking_utils/__init__.py && \
    ls -la bytetrack_yolox/ && \
    ls -la bytetrack_yolox/tracker/ && \
    echo "ByteTrack: パッケージ構造修正完了（パッケージ名変更）"

# アプリケーションファイルをコピー
COPY src/ /workspace/src/
COPY config.yml /workspace/
COPY configs/ /workspace/configs/
COPY test_environment.py /workspace/
COPY quick_test.py /workspace/

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