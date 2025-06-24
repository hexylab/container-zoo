# Express.js Backend テンプレート

Node.js + Express.js + MongoDB + Redisを使用したバックエンド開発環境のDockerテンプレートです。

## 含まれる主要コンポーネント

- **Node.js**: 20.x (Alpine Linux)
- **Express.js**: 4.18.x + セキュリティミドルウェア
- **MongoDB**: 7.0 + Mongo Express管理ツール
- **Redis**: 7.2 + Redis Commander管理ツール
- **開発ツール**: nodemon, TypeScript, ESLint, Prettier, Jest

## 必要な環境

- Docker
- Docker Compose

## セットアップ

### 1. リポジトリのクローンと移動
```bash
cd backend/nodejs/express
```

### 2. 環境変数ファイルの設定
```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
```

### 3. Dockerイメージのビルドと起動
```bash
# ビルドと起動
docker-compose up --build

# バックグラウンドで起動
docker-compose up -d
```

## 使用方法

### 開発サーバーの起動
```bash
# すべてのサービスを起動
docker-compose up

# バックエンドのみ起動
docker-compose up express-backend
```

### アクセス先
- **API サーバー**: http://localhost:3000
- **MongoDB管理**: http://localhost:8081 (admin/admin)
- **Redis管理**: http://localhost:8082

### 主要なAPIエンドポイント
- `GET /health` - ヘルスチェック
- `GET /api/info` - API情報
- `GET /api/users` - ユーザー一覧
- `POST /api/users` - ユーザー作成

## 環境テスト

```bash
# コンテナ内でテスト実行
docker-compose exec express-backend node test_environment.js
```

## 開発時の操作

### コンテナに入る
```bash
docker-compose exec express-backend bash
```

### ログの確認
```bash
# すべてのサービスのログ
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs -f express-backend
```

### パッケージの追加
```bash
# コンテナ内で実行
npm install package-name

# または、package.jsonを編集後に再ビルド
docker-compose down
docker-compose up --build
```

## デバッグ

### Node.js デバッガー
- デバッグポート: 9229
- VS Code等のIDEから接続可能

### ライブリロード
- `src/`ディレクトリの変更を自動検知
- nodemonによる自動再起動

## ディレクトリ構成

```
express/
├── Dockerfile              # Docker設定
├── docker-compose.yml      # Docker Compose設定
├── package.json            # Node.js依存関係
├── nodemon.json            # nodemon設定
├── test_environment.js     # 環境テストスクリプト
├── .env.example            # 環境変数テンプレート
├── README.md              # このファイル
└── src/
    └── index.js           # メインアプリケーション
```

## 主要な機能

### セキュリティ
- Helmet.js (セキュリティヘッダー)
- CORS設定
- レート制限
- 入力検証 (Joi)

### 認証・認可
- JWT認証 (実装例)
- bcrypt (パスワードハッシュ化)

### データベース
- MongoDB (Mongoose ODM)
- Redis (キャッシュ・セッション)

### 開発支援
- Express Async Errors
- Winston (構造化ログ)
- Morgan (HTTPリクエストログ)
- 圧縮対応

## カスタマイズ

### 環境変数
`.env`ファイルで以下の設定が可能：
- `NODE_ENV`: 実行環境
- `PORT`: サーバーポート
- `DB_URL`: MongoDB接続URL
- `REDIS_URL`: Redis接続URL
- `JWT_SECRET`: JWT秘密鍵

### 依存関係の追加
`package.json`にパッケージを追加後、再ビルドしてください。

### MongoDB初期データ
`mongo-init/`ディレクトリに初期化スクリプトを配置できます。

## トラブルシューティング

### ポートが使用中
```bash
# 使用中のポートを確認
lsof -i :3000

# 強制停止
docker-compose down --remove-orphans
```

### データベース接続エラー
```bash
# コンテナの状態確認
docker-compose ps

# MongoDB の状態確認
docker-compose logs mongo
```

### パフォーマンス問題
```bash
# リソース使用量確認
docker stats

# 不要なイメージ・コンテナの削除
docker system prune
```

## 本番環境への展開

1. `NODE_ENV=production`に設定
2. セキュリティ設定の強化
3. 環境変数の適切な設定
4. ヘルスチェックの設定
5. ログ収集の設定

## テンプレートとしての使用

このテンプレートを新しいプロジェクトで使用する場合：

1. ディレクトリをコピー
2. `package.json`のプロジェクト情報を更新
3. `.env`ファイルを設定
4. `src/index.js`を編集してビジネスロジックを実装

## ライセンス

MIT License