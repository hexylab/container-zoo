# Docker環境構築完了

## 日付・作業者
- 日付: 2025-06-28
- 作業: Docker環境ファイル作成完了

## 作成したファイル

### 1. Dockerfile
- ベースイメージ: nvidia/cuda:12.2.0-devel-ubuntu22.04
- 公式リポジトリクローン:
  - YOLOX: https://github.com/Megvii-BaseDetection/YOLOX
  - ByteTrack: https://github.com/ifzhang/ByteTrack
- CUDA対応、動画処理、開発環境完備

### 2. requirements.txt
- PyTorch, OpenCV, 数値計算ライブラリ
- YOLOX/ByteTrack依存関係
- 動画処理、設定管理、開発ツール
- ONNX Runtime GPU対応

### 3. docker-compose.yml
- 3つのサービス定義:
  - yolox-bytetrack-dev: メイン開発環境
  - jupyter: Jupyter Lab環境
  - tracking-server: ストリーミング対応（オプション）

## 特徴

### GPU対応
- NVIDIA Container Runtime使用
- 全GPU利用可能
- CUDA環境変数設定

### ボリュームマウント
- ソースコード: ./src → /workspace/src
- 設定ファイル: ./config.yml, ./configs
- データ: ./models, ./data, ./output
- 開発中の変更が即座に反映

### ポート設定
- 8888: Jupyter Lab (開発環境)
- 8890: Jupyter Lab (専用環境)
- 8000/8080: API/WebSocket (ストリーミング)
- 6006: TensorBoard

### デバイスアクセス
- Webカメラアクセス (/dev/video0)
- GPUアクセス (nvidia runtime)

## 使用方法

### 基本開発
```bash
docker-compose up yolox-bytetrack-dev
```

### Jupyter Lab
```bash
docker-compose up jupyter
# http://localhost:8890 でアクセス
```

### リアルタイム追跡
```bash
docker-compose up tracking-server
```

## 次のステップ
1. メインスクリプト作成 (src/main.py)
2. 設定読み込み (src/config_loader.py) 
3. YOLOX+ByteTrack統合 (src/yolox_tracker.py)
4. 環境テスト (test_environment.py)

## 設計のポイント
- 開発効率重視のボリュームマウント
- 用途別サービス分離
- 実用的なポート設定
- GPU環境の完全対応