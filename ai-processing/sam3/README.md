# SAM3 Docker環境

Meta SAM3 (Segment Anything Model 3) 用のDocker環境です。

## 概要

- **ベースイメージ**: `nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04`
- **Python**: 3.12
- **PyTorch**: 2.5.1
- **モデル**: `facebook/sam3`

## 前提条件

- Docker
- NVIDIA Container Toolkit
- NVIDIA GPU (CUDA 12.1対応)
- **Hugging Face Token** (必須 - ゲート付きモデル)

## セットアップ

### 1. Hugging Faceトークンの準備

SAM3はゲート付きモデルのため、アクセスにはトークンが必要です。

1. [Hugging Face Token](https://huggingface.co/settings/tokens) でトークンを取得
2. [facebook/sam3](https://huggingface.co/facebook/sam3) でモデルへのアクセスをリクエスト
3. `.env` ファイルを作成:

```bash
cp .env.example .env
# .env ファイルを編集して HF_TOKEN を設定
```

### 2. コンテナのビルド

```bash
docker build -t sam3 .
```

### 3. モデルのダウンロード

```bash
docker run --rm --env-file .env -v $(pwd)/models:/workspace/models sam3 python download_model.py
```

### 4. 環境テスト

```bash
docker run --rm --gpus all --env-file .env sam3 python test_environment.py
```

## Docker Composeでの起動

```bash
# .envファイルを作成してからdocker-compose up
cp .env.example .env
# .envを編集してHF_TOKENを設定

docker-compose up -d
docker-compose exec sam3 bash
```

## 使用例

```python
from transformers import AutoModel, AutoProcessor
from PIL import Image
import torch
import os

# モデルとプロセッサの読み込み
model_name = "facebook/sam3"
token = os.environ.get("HF_TOKEN")

processor = AutoProcessor.from_pretrained(model_name, token=token)
model = AutoModel.from_pretrained(model_name, token=token).cuda()

# 画像のセグメンテーション
image = Image.open("your_image.jpg")
inputs = processor(images=image, return_tensors="pt").to("cuda")

with torch.no_grad():
    outputs = model(**inputs)

print("セグメンテーション完了")
```

## ファイル構成

```
sam3/
├── Dockerfile           # Dockerイメージ定義
├── docker-compose.yml   # Docker Compose設定
├── requirements.txt     # Python依存関係
├── download_model.py    # モデルダウンロードスクリプト
├── test_environment.py  # 環境テストスクリプト
├── .env.example         # 環境変数テンプレート
└── README.md            # このファイル
```

## 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `HF_TOKEN` | Hugging Faceアクセストークン | **必須** |
| `HF_HOME` | Hugging Faceキャッシュディレクトリ | オプション |
| `CUDA_VISIBLE_DEVICES` | 使用するGPU | オプション |

## 注意事項

- **HF_TOKENは必須です** - SAM3はゲート付きモデルのため
- モデルへのアクセス許可を取得してからダウンロードしてください
- 初回起動時はモデルのダウンロードに時間がかかります
- `.env` ファイルはgitignoreに含まれており、リポジトリにコミットされません
