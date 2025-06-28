# YOLOX + ByteTrack テンプレート構造設計

## 日付・作業者
- 日付: 2025-06-28
- 作業: テンプレート構造設計

## 既存テンプレート分析結果

### cuda-tensorrtテンプレートの特徴
- **ベースイメージ**: nvidia/cuda:12.2.0-devel-ubuntu22.04
- **Python環境**: Python 3.10+ 
- **主要ライブラリ**: PyTorch, ONNX, TensorRT, OpenCV
- **構造パターン**: 
  - Dockerfile, docker-compose.yml, requirements.txt, README.md
  - test_environment.py (環境テスト)
  - workspace/, models/, data/, notebooks/ (データディレクトリ)

### パターン分析
1. **GPU対応**: runtime: nvidia設定
2. **ポート設定**: Jupyter用8888ポート
3. **ボリュームマウント**: 作業用ディレクトリマッピング
4. **環境変数**: NVIDIA_VISIBLE_DEVICES, PYTHONPATH等
5. **テストスクリプト**: インポート・CUDA・処理テスト

## yolox-bytetrackテンプレート設計

### ディレクトリ構造
```
ai-processing/yolox-bytetrack/
├── Dockerfile                   # YOLOX + ByteTrack環境
├── docker-compose.yml           # GPU設定、ボリューム
├── requirements.txt             # Python依存関係
├── README.md                    # 使用方法・設定説明
├── config.yml                   # メイン設定ファイル
├── configs/                     # 設定例集
│   ├── webcam.yml              # Webカメラ用設定
│   ├── video.yml               # 動画ファイル用設定
│   └── rtsp.yml                # RTSPストリーム用設定
├── src/                        # メインアプリケーション
│   ├── main.py                 # エントリーポイント
│   ├── yolox_tracker.py        # YOLOX + ByteTrack統合
│   ├── config_loader.py        # 設定ファイル読み込み
│   └── utils/                  # ユーティリティ
│       ├── video_utils.py      # 動画処理
│       └── visualization.py    # 描画・可視化
├── models/                     # モデルファイル格納
│   ├── yolox_s.pth            # YOLOXモデル（ダウンロード用）
│   └── README.md              # モデル取得方法
├── data/                       # 入力データ
│   ├── sample.mp4             # サンプル動画
│   └── README.md              # データ配置説明
├── output/                     # 出力結果
│   ├── videos/                # 結果動画
│   ├── tracking_data/         # 追跡データJSON
│   └── logs/                  # ログファイル
└── test_environment.py         # 環境テスト
```

### 既存テンプレートとの統一性
- **ファイル命名**: 既存パターンに準拠
- **ディレクトリ構造**: models/, data/, workspace/等の共通構造
- **Docker設定**: GPU設定、ポート設定の統一
- **テストスクリプト**: test_environment.py形式

### 拡張点
- **config.yml**: 設定駆動の実行（新機能）
- **configs/**: 用途別設定例（新機能）
- **src/**: 構造化されたソースコード（新機能）
- **output/**: 結果の種類別整理（新機能）

## 次のステップ
1. config.yml設計の詳細化
2. Dockerfile作成（cuda-tensorrtベース）
3. docker-compose.yml作成
4. requirements.txt作成（YOLOX, ByteTrack追加）

## 決定事項
- ✅ ディレクトリ構造を作成
- ✅ 既存テンプレートパターンを踏襲
- ✅ config.yml駆動の設計を採用
- ✅ 用途別設定例を提供する設計