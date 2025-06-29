# 公式リポジトリ使用決定

## 日付・作業者
- 日付: 2025-06-28
- 作業: 実装ソース決定

## 決定事項

### 使用する公式リポジトリ
1. **YOLOX**: https://github.com/Megvii-BaseDetection/YOLOX
2. **ByteTrack**: https://github.com/ifzhang/ByteTrack

### 理由
- 最新・公式実装の使用
- カスタマイズ・デバッグの容易さ
- コミュニティサポート
- 機能制限なし

### 実装方針
```dockerfile
# YOLOX公式リポジトリ
RUN git clone https://github.com/Megvii-BaseDetection/YOLOX.git /workspace/YOLOX
RUN cd /workspace/YOLOX && pip install -e .

# ByteTrack公式リポジトリ
RUN git clone https://github.com/ifzhang/ByteTrack.git /workspace/ByteTrack
RUN cd /workspace/ByteTrack && pip install -r requirements.txt
```

### 注意点
- Dockerイメージサイズが大きくなる
- ビルド時間が長くなる
- バージョン固定の考慮が必要

### 対応策
- .dockerignoreでビルド最適化
- マルチステージビルドの検討
- 特定コミットでのclone