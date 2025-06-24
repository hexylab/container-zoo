# 開発用Dockerテンプレート集

AI画像処理、バックエンドAPI、フロントエンドアプリケーション開発用の汎用的なDockerテンプレート集です。新しいプロジェクトでテンプレートとして再利用できるよう設計されています。

## ディレクトリ構成

```
dev_docker/
├── README.md                    # このファイル
├── docker-compose.yml           # メインのDocker Compose設定
│
├── ai-processing/              # AI・機械学習環境
│   ├── cuda-tensorrt/          # CUDA + TensorRT + ONNX 映像処理環境 (完成)
│   ├── opencv/                 # OpenCV画像処理環境
│   ├── pytorch/                # PyTorch機械学習環境
│   └── tensorflow/             # TensorFlow機械学習環境
│
├── backend/                    # バックエンドAPI環境
│   ├── nodejs/
│   │   ├── express/            # Express.js + MongoDB + Redis (完成)
│   │   ├── fastify/            # Fastify.js 高速API
│   │   └── nestjs/            # NestJS エンタープライズ
│   ├── python/
│   │   ├── fastapi/           # FastAPI + PostgreSQL
│   │   └── django/            # Django ORM + PostgreSQL
│   └── golang/
│       ├── gin/               # Gin Web Framework
│       └── fiber/             # Fiber 高速API
│
├── frontend/                   # フロントエンド環境
│   ├── react/
│   │   ├── mui/               # React + Material-UI
│   │   ├── nextjs/            # Next.js フルスタック
│   │   └── tailwind/          # React + Tailwind CSS
│   ├── vue/
│   │   ├── nuxt/              # Nuxt.js
│   │   └── vuetify/           # Vue + Vuetify
│   └── angular/
│       ├── material/          # Angular + Material
│       └── standalone/        # Angular Standalone
│
├── database/                   # データベース環境
│   ├── mongodb/               # MongoDB + レプリケーション
│   ├── postgresql/            # PostgreSQL + pgAdmin
│   └── redis/                 # Redis + Redis Commander
│
├── tools/                      # 開発支援ツール
│   ├── nginx/                 # リバースプロキシ
│   ├── caddy/                 # 自動HTTPS
│   └── monitoring/            # Prometheus + Grafana
│
├── templates/                  # プロジェクトテンプレート
│   ├── fullstack-react-express/  # React + Express フルスタック
│   ├── ai-jupyter-lab/           # Jupyter Lab AI研究環境
│   └── microservices/            # マイクロサービス構成
│
├── base/                       # ベースイメージ
│   ├── alpine-dev/            # Alpine Linux開発環境
│   └── ubuntu-dev/            # Ubuntu開発環境
│
└── scripts/                    # 自動化スクリプト
    ├── build-all.sh           # 全イメージビルド
    ├── clean.sh               # 不要リソース削除
    └── init-project.sh        # プロジェクト初期化
```

## クイックスタート

### 1. 個別環境の起動

```bash
# CUDA + TensorRT AI環境
cd ai-processing/cuda-tensorrt
docker-compose up -d

# Express.js バックエンド
cd backend/nodejs/express  
docker-compose up -d

# React + MUI フロントエンド
cd frontend/react/mui
docker-compose up -d
```

### 2. フルスタック開発環境

```bash
# React + Express フルスタック
cd templates/fullstack-react-express
docker-compose up -d
```

### 3. 一括ビルド

```bash
# すべてのイメージをビルド
./scripts/build-all.sh

# 不要なリソースをクリーンアップ
./scripts/clean.sh
```

## 利用可能なテンプレート

### 動作確認済み

| テンプレート | 説明 | ポート | 管理ツール |
|-------------|------|--------|-----------|
| **cuda-tensorrt** | CUDA + TensorRT + ONNX + PyTorch | 8888 | Jupyter Lab |
| **express** | Express.js + MongoDB + Redis | 3000 | Mongo Express (8081), Redis Commander (8082) |

### 準備中

- React + Material-UI フロントエンド
- FastAPI + PostgreSQL バックエンド
- Django + PostgreSQL バックエンド
- Next.js フルスタック
- Vue.js + Nuxt.js
- Angular + Material
- Gin + PostgreSQL (Go)
- Fiber API (Go)

## 各テンプレートの詳細

### AI・機械学習環境

#### CUDA + TensorRT (ai-processing/cuda-tensorrt/)
- **用途**: 映像処理、物体検出、深層学習推論
- **含まれる技術**: CUDA 12.2, TensorRT 8.6+, PyTorch, ONNX Runtime
- **GPU要件**: NVIDIA GPU (CUDA対応)
- **アクセス**: http://localhost:8888 (Jupyter Lab)

### バックエンドAPI環境

#### Express.js (backend/nodejs/express/)
- **用途**: REST API, リアルタイム通信, マイクロサービス
- **含まれる技術**: Express.js 4.18+, MongoDB 7.0, Redis 7.2
- **セキュリティ**: Helmet, CORS, レート制限, JWT認証
- **アクセス**: http://localhost:3000 (API)

## テンプレートの使用方法

### 新規プロジェクトでの使用

1. **テンプレートをコピー**
   ```bash
   cp -r ai-processing/cuda-tensorrt my-ai-project
   cd my-ai-project
   ```

2. **設定をカスタマイズ**
   ```bash
   # 環境変数を設定
   cp .env.example .env
   vim .env
   
   # Docker Compose設定を編集
   vim docker-compose.yml
   ```

3. **プロジェクト固有の実装**
   ```bash
   # ビルドして起動
   docker-compose up --build
   ```

### ベースイメージとしての使用

```dockerfile
# 既存のテンプレートをベースに使用
FROM cuda-tensorrt-dev:latest

# プロジェクト固有の依存関係を追加
COPY requirements.txt .
RUN pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . .
```

## ネットワーク構成

各テンプレートは独立したネットワークで動作しますが、必要に応じて相互接続可能です：

```yaml
# docker-compose.yml での連携例
networks:
  ai-network:
    external: true
  backend-network:
    external: true
```

## リソース要件

| テンプレート | CPU | メモリ | ストレージ | GPU |
|-------------|-----|--------|-----------|-----|
| cuda-tensorrt | 4+ cores | 8GB+ | 20GB+ | NVIDIA CUDA |
| express | 2+ cores | 2GB+ | 5GB+ | 不要 |
| react-mui | 2+ cores | 1GB+ | 3GB+ | 不要 |

## トラブルシューティング

### よくある問題

1. **ポート競合**
   ```bash
   # 使用中のポートを確認
   lsof -i :3000
   
   # Docker Composeでポートを変更
   ports:
     - "3001:3000"
   ```

2. **GPU認識されない (CUDA環境)**
   ```bash
   # NVIDIA Container Toolkit の確認
   docker run --rm --gpus all nvidia/cuda:12.2-base-ubuntu22.04 nvidia-smi
   ```

3. **メモリ不足**
   ```bash
   # Dockerのリソース制限を確認
   docker system df
   docker system prune
   ```

### ログ確認

```bash
# 全サービスのログ
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f service-name

# エラーログのみ
docker-compose logs --tail=50 service-name | grep ERROR
```

## 関連リンク

- [Docker公式ドキュメント](https://docs.docker.com/)
- [Docker Compose公式ガイド](https://docs.docker.com/compose/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)

---

**最終更新**: 2025-06-24  
**バージョン**: 1.0.0