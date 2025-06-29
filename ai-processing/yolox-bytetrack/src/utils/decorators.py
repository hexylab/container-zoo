#!/usr/bin/env python3
"""
共通デコレータ
エラーハンドリングとログ出力を統一化
"""

import functools
import logging
import time
from typing import Callable, Any
from .exceptions import ComponentInitializationError


def handle_initialization(component_name: str):
    """
    初期化エラーハンドリングデコレータ
    
    Args:
        component_name: コンポーネント名
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            logger = getattr(self, 'logger', logging.getLogger(__name__))
            
            try:
                logger.info(f"{component_name}初期化開始")
                result = func(self, *args, **kwargs)
                logger.info(f"{component_name}初期化完了")
                return result
            except Exception as e:
                logger.error(f"{component_name}初期化失敗: {e}")
                raise ComponentInitializationError(f"{component_name}初期化失敗: {e}")
        return wrapper
    return decorator


def handle_processing(operation_name: str, error_class: type = RuntimeError):
    """
    処理エラーハンドリングデコレータ
    
    Args:
        operation_name: 処理名
        error_class: 発生させる例外クラス
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            logger = getattr(self, 'logger', logging.getLogger(__name__))
            
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"{operation_name}失敗: {e}")
                raise error_class(f"{operation_name}失敗: {e}")
        return wrapper
    return decorator


def log_performance(operation_name: str, log_level: int = logging.DEBUG):
    """
    パフォーマンス測定デコレータ
    
    Args:
        operation_name: 処理名
        log_level: ログレベル
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            logger = getattr(self, 'logger', logging.getLogger(__name__))
            
            start_time = time.time()
            try:
                result = func(self, *args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(log_level, f"{operation_name}: {elapsed*1000:.1f}ms")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.log(log_level, f"{operation_name}(失敗): {elapsed*1000:.1f}ms")
                raise
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    失敗時リトライデコレータ
    
    Args:
        max_retries: 最大リトライ回数
        delay: リトライ間隔(秒)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            logger = getattr(self, 'logger', logging.getLogger(__name__))
            
            for attempt in range(max_retries + 1):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} 最大リトライ回数到達: {e}")
                        raise
                    else:
                        logger.warning(f"{func.__name__} リトライ {attempt + 1}/{max_retries}: {e}")
                        time.sleep(delay)
        return wrapper
    return decorator


def validate_input(*validators):
    """
    入力バリデーションデコレータ
    
    Args:
        validators: バリデーター関数のタプル
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # バリデーター実行
            for validator in validators:
                validator(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator