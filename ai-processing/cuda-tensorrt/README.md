# CUDA + TensorRT + ONNX 映像処理環境

Ubuntu 22.04ベースで、CUDA、TensorRT、Python、ONNXを使った映像処理が可能なDocker環境です。

## 含まれる主要コンポーネント

- **OS**: Ubuntu 22.04
- **CUDA**: 12.2 (nvidia/cuda:12.2-devel-ubuntu22.04)
- **Python**: 3.10+
- **TensorRT**: 8.6+
- **ONNX**: 1.14+
- **OpenCV**: 4.8+ (動画処理対応)
- **PyTorch**: 2.0+ (CUDA対応)

## 必要な環境

- Docker
- Docker Compose
- NVIDIA Docker Runtime
- NVIDIA GPU (CUDA対応)

## セットアップ

### 1. リポジトリのクローンと移動
```bash
cd ai-processing/cuda-tensorrt
```

### 2. ワークスペースディレクトリの作成
```bash
mkdir -p workspace models data notebooks
```

### 3. Dockerイメージのビルド
```bash
docker-compose build
```

### 4. コンテナの起動（対話モード）
```bash
docker-compose run --rm cuda-tensorrt-dev
```

### 5. Jupyter環境での起動
```bash
docker-compose up jupyter
```
Jupyter Labは http://localhost:8890 でアクセス可能

## 環境テスト

コンテナ内で以下のコマンドを実行して環境が正しく構築されているかテストできます：

```bash
python3 test_environment.py
```

## 使用例

### 基本的な使用方法
```bash
# コンテナに入る
docker-compose run --rm cuda-tensorrt-dev bash

# Python実行
python3 your_script.py

# Jupyter起動
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

### GPUの確認
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
print(f"GPU name: {torch.cuda.get_device_name(0)}")
```

### ONNX Runtime GPU確認
```python
import onnxruntime as ort
providers = ort.get_available_providers()
print("Available providers:", providers)
```

## ディレクトリ構成

```
cuda-tensorrt/
├── Dockerfile              # Docker設定
├── docker-compose.yml      # Docker Compose設定
├── requirements.txt        # Pythonパッケージ
├── test_environment.py     # 環境テストスクリプト
├── README.md              # このファイル
├── workspace/             # プロジェクト作業ディレクトリ
├── models/                # モデルファイル保存用
├── data/                  # データファイル保存用
└── notebooks/             # Jupyterノートブック用
```

## トラブルシューティング

### GPU認識されない場合
```bash
# NVIDIA Docker Runtimeの確認
docker run --rm --gpus all nvidia/cuda:12.2-base-ubuntu22.04 nvidia-smi
```

### パッケージインストールエラー
```bash
# コンテナ内でアップデート
apt-get update && apt-get upgrade -y
pip3 install --upgrade pip
```

### TensorRT関連エラー
```bash
# TensorRTライブラリパスの確認
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```

## カスタマイズ

- `requirements.txt`: 必要なPythonパッケージを追加
- `Dockerfile`: システムレベルの設定変更
- `docker-compose.yml`: ポートやボリューム設定の調整