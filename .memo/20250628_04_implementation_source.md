# YOLOX + ByteTrack 実装ソース検討

## 日付・作業者
- 日付: 2025-06-28  
- 作業: 実装元の検討・決定

## 検討する選択肢

### YOLOX取得方法
1. **公式リポジトリ**: https://github.com/Megvii-BaseDetection/YOLOX
   - 最新・公式実装
   - Git clone → pip install -e .
   
2. **pip版**: pip install yolox
   - 簡単インストール
   - バージョン固定可能
   
3. **Ultralytics統合版**: ultralytics package経由
   - YOLOv8と統一インターフェース
   - pip install ultralytics

### ByteTrack取得方法
1. **公式リポジトリ**: https://github.com/ifzhang/ByteTrack
   - 最新・公式実装
   - Git clone → 手動インストール
   
2. **第三者実装**: 
   - pip install byte-tracker等
   - メンテナンス状況要確認

## 各方法の比較

### 方法A: 公式リポジトリ使用（推奨）
```dockerfile
# YOLOX公式
RUN git clone https://github.com/Megvii-BaseDetection/YOLOX.git /workspace/YOLOX
RUN cd /workspace/YOLOX && pip install -e .

# ByteTrack公式  
RUN git clone https://github.com/ifzhang/ByteTrack.git /workspace/ByteTrack
RUN cd /workspace/ByteTrack && pip install -r requirements.txt
```

**メリット**:
- 最新・公式実装
- コミュニティサポート
- カスタマイズ容易

**デメリット**:
- Dockerイメージサイズ増大
- バージョン管理複雑

### 方法B: pip版使用
```dockerfile
RUN pip install yolox ultralytics
# ByteTrackは公式pip版なし
```

**メリット**:
- 簡単インストール
- 小さなイメージサイズ

**デメリット**:
- ByteTrackの公式pip版なし
- 機能制限の可能性

## 推奨アプローチ

### ハイブリッド方式
- **YOLOX**: pip install yolox (安定版)
- **ByteTrack**: Git clone公式リポジトリ（最新）

### 理由
1. YOLOXはpip版が安定している
2. ByteTrackは公式リポジトリが必要
3. バランスの取れたアプローチ

## 質問への回答
はい、基本的に公式Gitリポジトリ使用が適切です。特にByteTrackは公式リポジトリからの取得が必要です。