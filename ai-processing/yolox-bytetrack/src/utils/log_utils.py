#!/usr/bin/env python3
"""
ログ管理ユーティリティ
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = __name__, 
                log_file: Optional[Union[str, Path]] = None,
                log_level: str = "INFO",
                console_output: bool = True,
                file_output: bool = True,
                max_bytes: int = 10 * 1024 * 1024,  # 10MB
                backup_count: int = 5) -> logging.Logger:
    """
    ログ設定を行い、ロガーを返す
    
    Args:
        name: ロガー名
        log_file: ログファイルパス
        log_level: ログレベル
        console_output: コンソール出力の有無
        file_output: ファイル出力の有無
        max_bytes: ログファイルの最大サイズ
        backup_count: バックアップファイル数
        
    Returns:
        logging.Logger: 設定済みロガー
    """
    # ロガー作成
    logger = logging.getLogger(name)
    
    # 既存のハンドラーをクリア（重複防止）
    logger.handlers.clear()
    
    # ログレベル設定
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # フォーマット設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソール出力
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # ファイル出力
    if file_output and log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_system_info(logger: logging.Logger):
    """システム情報をログ出力"""
    import platform
    import psutil
    import torch
    
    logger.info("=== システム情報 ===")
    logger.info(f"OS: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"CPU: {psutil.cpu_count()} cores")
    logger.info(f"メモリ: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    
    # GPU情報
    if torch.cuda.is_available():
        logger.info(f"CUDA: {torch.version.cuda}")
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
    else:
        logger.info("CUDA: 利用不可")
    
    logger.info("==================")


def log_config_summary(logger: logging.Logger, config):
    """設定サマリーをログ出力"""
    logger.info("=== 設定サマリー ===")
    logger.info(f"入力タイプ: {config.input.type}")
    logger.info(f"入力ソース: {config.input.source}")
    logger.info(f"YOLOXモデル: {config.yolox.model_size}")
    logger.info(f"信頼度閾値: {config.yolox.confidence_threshold}")
    logger.info(f"追跡閾値: {config.bytetrack.track_thresh}")
    logger.info(f"動画保存: {config.output.save_video}")
    logger.info(f"追跡データ保存: {config.output.save_tracking_data}")
    logger.info(f"リアルタイム表示: {config.display.show_realtime}")
    logger.info("==================")


class LogCapture:
    """ログメッセージのキャプチャクラス"""
    
    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        self.logger = logger
        self.level = level
        self.messages = []
        self.handler = None
    
    def start_capture(self):
        """ログキャプチャ開始"""
        self.handler = LogHandler(self.messages)
        self.handler.setLevel(self.level)
        self.logger.addHandler(self.handler)
    
    def stop_capture(self):
        """ログキャプチャ停止"""
        if self.handler:
            self.logger.removeHandler(self.handler)
            self.handler = None
    
    def get_messages(self) -> list:
        """キャプチャしたメッセージを取得"""
        return self.messages.copy()
    
    def clear_messages(self):
        """メッセージをクリア"""
        self.messages.clear()
    
    def __enter__(self):
        self.start_capture()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_capture()


class LogHandler(logging.Handler):
    """カスタムログハンドラー"""
    
    def __init__(self, message_list: list):
        super().__init__()
        self.message_list = message_list
    
    def emit(self, record):
        """ログレコードの処理"""
        message = self.format(record)
        self.message_list.append({
            'timestamp': record.created,
            'level': record.levelname,
            'message': message,
            'module': record.module
        })


class PerformanceLogger:
    """パフォーマンス測定・ログクラス"""
    
    def __init__(self, logger: logging.Logger, log_interval: int = 100):
        self.logger = logger
        self.log_interval = log_interval
        self.stats = {
            'frame_count': 0,
            'total_inference_time': 0,
            'total_tracking_time': 0,
            'total_processing_time': 0
        }
        import time
        self.start_time = time.time()
    
    def log_frame_stats(self, inference_time: float, tracking_time: float, total_time: float):
        """フレーム処理統計をログ"""
        self.stats['frame_count'] += 1
        self.stats['total_inference_time'] += inference_time
        self.stats['total_tracking_time'] += tracking_time
        self.stats['total_processing_time'] += total_time
        
        # 定期的な統計出力
        if self.stats['frame_count'] % self.log_interval == 0:
            self._log_performance_summary()
    
    def _log_performance_summary(self):
        """パフォーマンスサマリーをログ出力"""
        import time
        
        count = self.stats['frame_count']
        elapsed = time.time() - self.start_time
        fps = count / elapsed if elapsed > 0 else 0
        
        avg_inference = self.stats['total_inference_time'] / count if count > 0 else 0
        avg_tracking = self.stats['total_tracking_time'] / count if count > 0 else 0
        avg_total = self.stats['total_processing_time'] / count if count > 0 else 0
        
        self.logger.info(
            f"Performance [{count} frames]: "
            f"FPS={fps:.2f}, "
            f"Inference={avg_inference*1000:.1f}ms, "
            f"Tracking={avg_tracking*1000:.1f}ms, "
            f"Total={avg_total*1000:.1f}ms"
        )
    
    def get_final_summary(self) -> dict:
        """最終パフォーマンスサマリーを取得"""
        import time
        
        count = self.stats['frame_count']
        elapsed = time.time() - self.start_time
        
        return {
            'total_frames': count,
            'total_time': elapsed,
            'average_fps': count / elapsed if elapsed > 0 else 0,
            'average_inference_time': self.stats['total_inference_time'] / count if count > 0 else 0,
            'average_tracking_time': self.stats['total_tracking_time'] / count if count > 0 else 0,
            'average_processing_time': self.stats['total_processing_time'] / count if count > 0 else 0
        }
    
    def log_final_summary(self):
        """最終サマリーをログ出力"""
        summary = self.get_final_summary()
        
        self.logger.info("=== 最終パフォーマンスサマリー ===")
        self.logger.info(f"総フレーム数: {summary['total_frames']}")
        self.logger.info(f"総処理時間: {summary['total_time']:.2f}秒")
        self.logger.info(f"平均FPS: {summary['average_fps']:.2f}")
        self.logger.info(f"平均推論時間: {summary['average_inference_time']*1000:.1f}ms")
        self.logger.info(f"平均追跡時間: {summary['average_tracking_time']*1000:.1f}ms")
        self.logger.info(f"平均処理時間: {summary['average_processing_time']*1000:.1f}ms")
        self.logger.info("===============================")