# Container Zoo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![NVIDIA CUDA](https://img.shields.io/badge/CUDA-12.2-76B900?logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![Node.js](https://img.shields.io/badge/Node.js-20-339933?logo=node.js&logoColor=white)](https://nodejs.org/)

ビルド可能なDockerfileのテンプレート集です。様々なプロジェクトで再利用できます。

## 収録コンテナ

| カテゴリ | 名前 | ベースイメージ | 用途 |
|---------|------|---------------|------|
| AI処理 | [cuda-tensorrt](./ai-processing/cuda-tensorrt/) | nvidia/cuda:12.2.0-devel-ubuntu22.04 | GPU推論・TensorRT開発環境 |
| バックエンド | [express](./backend/nodejs/express/) | node:20-alpine | Node.js Express開発環境 |

## 使い方

### 1. コンテナをビルドする

```bash
cd ai-processing/cuda-tensorrt
docker build -t cuda-tensorrt .
```

### 2. プロジェクトにコピーして使う

```bash
cp -r backend/nodejs/express /path/to/your/project
cd /path/to/your/project
docker build -t my-app .
```

### 3. docker-composeで起動する

各ディレクトリに `docker-compose.yml` が含まれています。

```bash
cd backend/nodejs/express
docker-compose up -d
```

## コンテナ詳細

### cuda-tensorrt

NVIDIA GPU を使用したAI推論・開発環境。

- CUDA 12.2 + TensorRT
- Python 3 + PyTorch / TensorFlow対応
- OpenCV + FFmpeg
- JupyterLab

**前提条件**: NVIDIA Container Toolkit

### express

Node.js Express の開発環境。

- Node.js 20 (Alpine)
- 開発ツール: nodemon, TypeScript
- ホットリロード対応
- デバッグポート (9229) 対応

## ライセンス

このリポジトリのDockerfile・スクリプトは MIT License で提供されています。

ただし、ビルドされるコンテナには各ベースイメージおよびパッケージのライセンスが適用されます：

| コンテナ | ベースイメージ | ライセンス |
|---------|---------------|-----------|
| cuda-tensorrt | nvidia/cuda | [NVIDIA Deep Learning Container License](https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license) |
| express | node:alpine | [Node.js License](https://github.com/nodejs/node/blob/main/LICENSE) (MIT) |

利用時は各ライセンスの条項をご確認ください。
