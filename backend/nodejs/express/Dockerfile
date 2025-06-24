FROM node:20-alpine

# 環境変数設定
ENV NODE_ENV=development
ENV NPM_CONFIG_LOGLEVEL=warn
ENV DEBIAN_FRONTEND=noninteractive

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージ更新（Alpine用）
RUN apk update && apk add --no-cache \
    git \
    bash \
    curl \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# パッケージファイルをコピー
COPY package*.json ./

# Node.js依存関係のインストール
RUN npm install

# アプリケーションコードをコピー
COPY . .

# 開発時に必要なグローバルツール
RUN npm install -g \
    nodemon \
    ts-node \
    typescript \
    @types/node

# ポート設定
EXPOSE 3000
EXPOSE 3001

# デバッグポート
EXPOSE 9229

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# 開発時のコマンド（デバッグモード対応）
CMD ["npm", "run", "dev"]