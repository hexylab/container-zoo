# YOLOX + ByteTrack 物体検出・追跡テンプレート

YOLOX物体検出とByteTrack追跡を組み合わせた、高性能リアルタイム物体検出・追跡システムのDockerテンプレートです。

## 特徴

- **高性能**: YOLOX + ByteTrack による高精度検出・追跡
- **設定駆動**: YAML設定ファイルによる柔軟な設定変更
- **多様な入力**: Webカメラ、動画ファイル、RTSPストリーム対応
- **豊富な出力**: 動画、追跡データ、フレーム画像、ログ出力
- **リアルタイム**: ライブ表示とFPS制御
- **GPU最適化**: CUDA対応による高速処理

## 必要環境

- Docker & Docker Compose
- NVIDIA Docker Runtime（GPU使用時）
- NVIDIA GPU（CUDA対応、推奨）

## クイックスタート

### 1. 環境構築

```bash
# リポジトリクローン
cd ai-processing/yolox-bytetrack

# Dockerイメージビルド
docker-compose build

# 環境テスト実行
docker-compose run --rm yolox-bytetrack-dev python test_environment.py
```

### 2. 基本実行

```bash
# Webカメラ（リアルタイム）
docker-compose run --rm yolox-bytetrack-dev python src/main.py --config configs/webcam.yml

# 動画ファイル処理
docker-compose run --rm yolox-bytetrack-dev python src/main.py --config configs/video.yml

# RTSPストリーム
docker-compose run --rm yolox-bytetrack-dev python src/main.py --config configs/rtsp.yml
```

### 3. Jupyter Lab（開発・研究用）

```bash
docker-compose up jupyter
# http://localhost:8890 でアクセス
```

## 設定ファイル

### メイン設定 (config.yml)

全設定項目を含む包括的な設定ファイル：

```yaml
# 入力設定
input:
  type: "video"  # webcam, video, rtsp, images
  source: "data/sample.mp4"
  fps_limit: 30

# YOLOX設定
yolox:
  model_size: "yolox_s"  # nano, tiny, s, m, l, x
  confidence_threshold: 0.5
  nms_threshold: 0.45

# ByteTrack設定
bytetrack:
  track_thresh: 0.5
  match_thresh: 0.8
  track_buffer: 30

# 出力設定
output:
  save_video: true
  save_tracking_data: true
  video_path: "output/videos/result_{timestamp}.mp4"
```

### 用途別設定例

- **`configs/webcam.yml`**: Webカメラ用（リアルタイム最適化）
- **`configs/video.yml`**: 動画ファイル用（高精度処理）
- **`configs/rtsp.yml`**: IPカメラ・監視用（長時間安定動作）

## 使用方法

### コマンドライン引数

```bash
python src/main.py [オプション]

必須:
  --config CONFIG    設定ファイルパス

オプション:
  --debug           デバッグモード有効化
  --benchmark       推論速度ベンチマーク実行
  --no-display      リアルタイム表示無効化
  --output-dir DIR  出力ディレクトリ上書き
```

### 使用例

```bash
# 基本実行
python src/main.py --config config.yml

# デバッグモード
python src/main.py --config configs/webcam.yml --debug

# バッチ処理（表示なし）
python src/main.py --config configs/video.yml --no-display

# ベンチマーク
python src/main.py --config config.yml --benchmark

# 出力先変更
python src/main.py --config config.yml --output-dir /custom/output
```

## 出力形式

### 1. 結果動画
- パス: `output/videos/result_{timestamp}.mp4`
- 追跡結果が描画された動画ファイル
- バウンディングボックス、追跡ID、軌跡表示

### 2. 追跡データ (JSON)
```json
{
  "metadata": {
    "total_frames": 1000,
    "processing_timestamp": "2025-06-28T10:30:00"
  },
  "statistics": {
    "total_tracks": 25,
    "avg_track_length": 45.2,
    "processing_fps": 28.5
  },
  "tracking_data": [
    {
      "frame_id": 1,
      "tracks": [
        {
          "track_id": 1,
          "bbox": [100, 50, 200, 150],
          "score": 0.85,
          "class_id": 0
        }
      ]
    }
  ]
}
```

### 3. ログファイル
- パス: `output/logs/log_{timestamp}.txt`
- 処理統計、エラー情報、パフォーマンス測定

## パフォーマンス

### 推奨スペック

| モデル | GPU | 処理速度 | 用途 |
|--------|-----|----------|------|
| yolox_nano | GTX 1060 | ~60 FPS | リアルタイム |
| yolox_s | RTX 3060 | ~45 FPS | バランス |
| yolox_m | RTX 3080 | ~35 FPS | 高精度 |
| yolox_l | RTX 4080 | ~25 FPS | 最高精度 |

### ベンチマーク実行

```bash
python src/main.py --config config.yml --benchmark
```

## トラブルシューティング

### 環境問題の診断

```bash
# 環境テスト実行
python test_environment.py

# GPU確認
docker run --rm --gpus all nvidia/cuda:12.2-base-ubuntu22.04 nvidia-smi
```

### よくある問題

#### 1. GPU認識されない
```bash
# NVIDIA Docker Runtime確認
docker info | grep nvidia

# runtime設定を確認
# /etc/docker/daemon.json に以下を追加:
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

#### 2. メモリ不足
```bash
# メモリ使用量確認
docker stats

# 軽量モデル使用
# config.yml で model_size: "yolox_nano" に変更
```

#### 3. カメラアクセスエラー
```bash
# デバイス確認
ls /dev/video*

# カメラ権限確認
docker-compose run --rm --device=/dev/video0 yolox-bytetrack-dev
```

## 開発・カスタマイズ

### ディレクトリ構造
```
yolox-bytetrack/
├── Dockerfile              # Docker環境定義
├── docker-compose.yml      # サービス設定
├── requirements.txt        # Python依存関係
├── config.yml             # メイン設定
├── configs/               # 用途別設定
├── src/                   # ソースコード
│   ├── main.py           # メインスクリプト
│   ├── config_loader.py  # 設定管理
│   ├── yolox_wrapper.py  # YOLOX統合
│   ├── bytetrack_wrapper.py # ByteTrack統合
│   ├── video_processor.py   # 動画処理
│   └── utils/            # ユーティリティ
├── models/               # モデルファイル
├── data/                # 入力データ
├── output/              # 出力結果
└── test_environment.py  # 環境テスト
```

### 新しい設定追加

1. `configs/` に新しいYAMLファイル作成
2. 必要に応じて入力・出力パラメータ調整
3. 用途に応じたモデルサイズ選択

### カスタムモデル対応

1. `models/` ディレクトリにモデルファイル配置
2. `config.yml` の `model_path` を更新
3. 必要に応じて `input_size` 調整

## ライセンス

このテンプレートは開発用途のみで提供されています。
- YOLOX: Apache License 2.0
- ByteTrack: MIT License

## 参考リンク

- [YOLOX公式リポジトリ](https://github.com/Megvii-BaseDetection/YOLOX)
- [ByteTrack公式リポジトリ](https://github.com/ifzhang/ByteTrack)
- [Docker公式ドキュメント](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)

---

**最終更新**: 2025-06-28  
**バージョン**: 1.0.0