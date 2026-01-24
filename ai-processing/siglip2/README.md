# SigLIP2 Docker環境

Google SigLIP2 (Sigmoid Loss for Language Image Pre-Training 2) モデル用のDocker環境です。

## 概要

- **ベースイメージ**: `nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04`
- **Python**: 3.12
- **PyTorch**: 2.5.1
- **モデル**: `google/siglip2-base-patch16-256`

## 前提条件

- Docker
- NVIDIA Container Toolkit
- NVIDIA GPU (CUDA 12.1対応)

## セットアップ

### 1. コンテナのビルド

```bash
docker build -t siglip2 .
```

### 2. モデルのダウンロード

```bash
docker run --rm -v $(pwd)/models:/workspace/models siglip2 python download_model.py
```

### 3. 環境テスト

```bash
docker run --rm --gpus all siglip2 python test_environment.py
```

## Docker Composeでの起動

```bash
docker-compose up -d
docker-compose exec siglip2 bash
```

## 使用例

```python
from transformers import AutoModel, AutoProcessor
from PIL import Image
import torch

# モデルとプロセッサの読み込み
model_name = "google/siglip2-base-patch16-256"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).cuda()

# 画像の特徴量抽出
image = Image.open("your_image.jpg")
inputs = processor(images=image, return_tensors="pt").to("cuda")

with torch.no_grad():
    features = model.get_image_features(**inputs)

print(f"特徴量shape: {features.shape}")
```

## ファイル構成

```
siglip2/
├── Dockerfile           # Dockerイメージ定義
├── docker-compose.yml   # Docker Compose設定
├── requirements.txt     # Python依存関係
├── download_model.py    # モデルダウンロードスクリプト
├── test_environment.py  # 環境テストスクリプト
├── .env.example         # 環境変数テンプレート
└── README.md            # このファイル
```

## 環境変数

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `HF_HOME` | Hugging Faceキャッシュディレクトリ | `/workspace/models/huggingface` |
| `CUDA_VISIBLE_DEVICES` | 使用するGPU | `0` |

## 注意事項

- SigLIP2はHugging Face Tokenなしでダウンロード可能です
- 初回起動時はモデルのダウンロードに時間がかかります
