#!/usr/bin/env python3
"""
共通例外クラス
アプリケーション全体で使用される例外を定義
"""

class YOLOXByteTrackError(Exception):
    """ベース例外クラス"""
    pass


class ComponentInitializationError(YOLOXByteTrackError):
    """コンポーネント初期化エラー"""
    pass


class ConfigValidationError(YOLOXByteTrackError):
    """設定バリデーションエラー"""
    pass


class VideoProcessingError(YOLOXByteTrackError):
    """動画処理エラー"""
    pass


class ModelLoadError(YOLOXByteTrackError):
    """モデル読み込みエラー"""
    pass


class InferenceError(YOLOXByteTrackError):
    """推論エラー"""
    pass