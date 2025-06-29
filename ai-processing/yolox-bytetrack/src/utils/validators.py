#!/usr/bin/env python3
"""
共通バリデーター関数
設定値検証を統一化
"""

from typing import Union, Any
from .exceptions import ConfigValidationError


def validate_threshold(value: float, name: str, min_val: float = 0.0, max_val: float = 1.0) -> None:
    """
    閾値バリデーション
    
    Args:
        value: 検証対象の値
        name: パラメータ名
        min_val: 最小値
        max_val: 最大値
        
    Raises:
        ConfigValidationError: 値が範囲外の場合
    """
    if not isinstance(value, (int, float)):
        raise ConfigValidationError(f"{name}は数値で指定してください: {value}")
    
    if not min_val <= value <= max_val:
        raise ConfigValidationError(
            f"{name}は {min_val}-{max_val} の範囲で指定してください: {value}"
        )


def validate_positive_integer(value: int, name: str) -> None:
    """
    正の整数バリデーション
    
    Args:
        value: 検証対象の値
        name: パラメータ名
        
    Raises:
        ConfigValidationError: 値が正の整数でない場合
    """
    if not isinstance(value, int):
        raise ConfigValidationError(f"{name}は整数で指定してください: {value}")
    
    if value <= 0:
        raise ConfigValidationError(f"{name}は正の値で指定してください: {value}")


def validate_positive_number(value: Union[int, float], name: str) -> None:
    """
    正の数値バリデーション
    
    Args:
        value: 検証対象の値
        name: パラメータ名
        
    Raises:
        ConfigValidationError: 値が正の数値でない場合
    """
    if not isinstance(value, (int, float)):
        raise ConfigValidationError(f"{name}は数値で指定してください: {value}")
    
    if value <= 0:
        raise ConfigValidationError(f"{name}は正の値で指定してください: {value}")


def validate_file_path(path: str, name: str, must_exist: bool = False) -> None:
    """
    ファイルパスバリデーション
    
    Args:
        path: ファイルパス
        name: パラメータ名
        must_exist: ファイルの存在確認をするか
        
    Raises:
        ConfigValidationError: パスが無効な場合
    """
    if not isinstance(path, str):
        raise ConfigValidationError(f"{name}は文字列で指定してください: {path}")
    
    if not path.strip():
        raise ConfigValidationError(f"{name}は空文字列にできません")
    
    if must_exist:
        from pathlib import Path
        if not Path(path).exists():
            raise ConfigValidationError(f"{name}が存在しません: {path}")


def validate_choice(value: Any, name: str, choices: list) -> None:
    """
    選択肢バリデーション
    
    Args:
        value: 検証対象の値
        name: パラメータ名
        choices: 有効な選択肢のリスト
        
    Raises:
        ConfigValidationError: 値が選択肢にない場合
    """
    if value not in choices:
        raise ConfigValidationError(
            f"{name}は次の中から選択してください {choices}: {value}"
        )


def validate_image_size(width: int, height: int, name: str = "画像サイズ") -> None:
    """
    画像サイズバリデーション
    
    Args:
        width: 幅
        height: 高さ
        name: パラメータ名
        
    Raises:
        ConfigValidationError: サイズが無効な場合
    """
    validate_positive_integer(width, f"{name}(幅)")
    validate_positive_integer(height, f"{name}(高さ)")
    
    # 実用的な制限値
    max_dimension = 10000
    if width > max_dimension or height > max_dimension:
        raise ConfigValidationError(
            f"{name}が大きすぎます。最大{max_dimension}px: {width}x{height}"
        )