#!/usr/bin/env python3
"""
設定ファイル読み込み・バリデーション・エラーハンドリング
config.ymlとサブ設定ファイルの読み込みを担当
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class InputConfig:
    """入力設定"""
    type: str
    source: Union[str, int]
    fps_limit: int = 30
    max_width: int = 1920
    max_height: int = 1080


@dataclass
class YOLOXConfig:
    """YOLOX設定"""
    model_size: str = "yolox_s"
    model_path: str = "models/yolox_s.pth"
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.45
    input_size: list = None
    target_classes: list = None
    device: str = "auto"
    
    def __post_init__(self):
        if self.input_size is None:
            self.input_size = [640, 640]
        if self.target_classes is None:
            self.target_classes = []


@dataclass
class ByteTrackConfig:
    """ByteTrack設定"""
    track_thresh: float = 0.5
    high_thresh: float = 0.6
    match_thresh: float = 0.8
    track_buffer: int = 30
    frame_rate: int = 30
    min_track_length: int = 10


@dataclass
class OutputConfig:
    """出力設定"""
    output_dir: str = "output"
    save_video: bool = True
    video_path: str = "output/videos/result_{timestamp}.mp4"
    video_codec: str = "mp4v"
    video_quality: int = 90
    save_tracking_data: bool = True
    tracking_data_path: str = "output/tracking_data/tracks_{timestamp}.json"
    save_frames: bool = False
    frames_dir: str = "output/frames/{timestamp}"
    frame_interval: int = 30
    save_logs: bool = True
    log_path: str = "output/logs/log_{timestamp}.txt"
    log_level: str = "INFO"


@dataclass
class DisplayConfig:
    """表示・可視化設定"""
    show_realtime: bool = True
    window_width: int = 1280
    window_height: int = 720
    draw_boxes: bool = True
    box_thickness: int = 2
    draw_track_ids: bool = True
    id_font_size: float = 0.8
    draw_trails: bool = True
    trail_length: int = 30
    show_stats: bool = True
    color_palette: str = "auto"


@dataclass
class PerformanceConfig:
    """パフォーマンス設定"""
    batch_size: int = 1
    num_workers: int = 4
    memory_efficient: bool = True
    stats_interval: int = 100


@dataclass
class DebugConfig:
    """デバッグ設定"""
    enabled: bool = False
    save_intermediate: bool = False
    enable_profiling: bool = False
    verbose: bool = False


@dataclass
class Config:
    """全体設定"""
    input: InputConfig
    yolox: YOLOXConfig
    bytetrack: ByteTrackConfig
    output: OutputConfig
    display: DisplayConfig
    performance: PerformanceConfig
    debug: DebugConfig


class ConfigValidationError(Exception):
    """設定バリデーションエラー"""
    pass


class ConfigLoader:
    """設定ファイルローダー"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """ログ設定"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def load_config(self, config_path: Union[str, Path]) -> Config:
        """
        設定ファイルを読み込み、バリデーション後にConfigオブジェクトを返す
        
        Args:
            config_path: 設定ファイルパス
            
        Returns:
            Config: 設定オブジェクト
            
        Raises:
            ConfigValidationError: 設定バリデーションエラー
            FileNotFoundError: ファイルが存在しない
            yaml.YAMLError: YAML解析エラー
        """
        config_path = Path(config_path)
        
        # ファイル存在確認
        if not config_path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")
        
        self.logger.info(f"設定ファイル読み込み開始: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"YAML解析エラー: {e}")
        
        # 設定バリデーション
        self._validate_config(config_dict)
        
        # Configオブジェクト作成
        config = self._create_config_objects(config_dict)
        
        # パス解決とディレクトリ作成
        self._resolve_paths(config)
        
        self.logger.info("設定ファイル読み込み完了")
        return config
    
    def _validate_config(self, config_dict: Dict[str, Any]) -> None:
        """設定バリデーション"""
        required_sections = ['input', 'yolox', 'bytetrack', 'output', 'display', 'performance', 'debug']
        
        for section in required_sections:
            if section not in config_dict:
                raise ConfigValidationError(f"必須セクション '{section}' が見つかりません")
        
        # 入力設定バリデーション
        self._validate_input_config(config_dict['input'])
        
        # YOLOX設定バリデーション
        self._validate_yolox_config(config_dict['yolox'])
        
        # ByteTrack設定バリデーション
        self._validate_bytetrack_config(config_dict['bytetrack'])
        
        # 出力設定バリデーション
        self._validate_output_config(config_dict['output'])
    
    def _validate_input_config(self, input_config: Dict[str, Any]) -> None:
        """入力設定バリデーション"""
        valid_types = ['webcam', 'video', 'rtsp', 'images', 'image']
        input_type = input_config.get('type')
        
        if input_type not in valid_types:
            raise ConfigValidationError(
                f"不正な入力タイプ: {input_type}. 有効な値: {valid_types}"
            )
        
        if 'source' not in input_config:
            raise ConfigValidationError("入力ソース 'source' が指定されていません")
    
    def _validate_yolox_config(self, yolox_config: Dict[str, Any]) -> None:
        """YOLOX設定バリデーション"""
        valid_sizes = ['yolox_nano', 'yolox_tiny', 'yolox_s', 'yolox_m', 'yolox_l', 'yolox_x']
        model_size = yolox_config.get('model_size', 'yolox_s')
        
        if model_size not in valid_sizes:
            raise ConfigValidationError(
                f"不正なモデルサイズ: {model_size}. 有効な値: {valid_sizes}"
            )
        
        # 閾値バリデーション
        conf_thresh = yolox_config.get('confidence_threshold', 0.5)
        if not 0.0 <= conf_thresh <= 1.0:
            raise ConfigValidationError(
                f"confidence_threshold は 0.0-1.0 の範囲で指定してください: {conf_thresh}"
            )
        
        nms_thresh = yolox_config.get('nms_threshold', 0.45)
        if not 0.0 <= nms_thresh <= 1.0:
            raise ConfigValidationError(
                f"nms_threshold は 0.0-1.0 の範囲で指定してください: {nms_thresh}"
            )
    
    def _validate_bytetrack_config(self, bytetrack_config: Dict[str, Any]) -> None:
        """ByteTrack設定バリデーション"""
        # 閾値バリデーション
        track_thresh = bytetrack_config.get('track_thresh', 0.5)
        if not 0.0 <= track_thresh <= 1.0:
            raise ConfigValidationError(
                f"track_thresh は 0.0-1.0 の範囲で指定してください: {track_thresh}"
            )
        
        match_thresh = bytetrack_config.get('match_thresh', 0.8)
        if not 0.0 <= match_thresh <= 1.0:
            raise ConfigValidationError(
                f"match_thresh は 0.0-1.0 の範囲で指定してください: {match_thresh}"
            )
        
        # 正数バリデーション
        track_buffer = bytetrack_config.get('track_buffer', 30)
        if track_buffer <= 0:
            raise ConfigValidationError(
                f"track_buffer は正の値で指定してください: {track_buffer}"
            )
    
    def _validate_output_config(self, output_config: Dict[str, Any]) -> None:
        """出力設定バリデーション"""
        valid_codecs = ['mp4v', 'XVID', 'H264', 'MJPG']
        codec = output_config.get('video_codec', 'mp4v')
        
        if codec not in valid_codecs:
            raise ConfigValidationError(
                f"不正な動画コーデック: {codec}. 有効な値: {valid_codecs}"
            )
        
        quality = output_config.get('video_quality', 90)
        if not 0 <= quality <= 100:
            raise ConfigValidationError(
                f"video_quality は 0-100 の範囲で指定してください: {quality}"
            )
        
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        log_level = output_config.get('log_level', 'INFO')
        if log_level not in valid_log_levels:
            raise ConfigValidationError(
                f"不正なログレベル: {log_level}. 有効な値: {valid_log_levels}"
            )
    
    def _create_config_objects(self, config_dict: Dict[str, Any]) -> Config:
        """設定辞書からConfigオブジェクトを作成"""
        return Config(
            input=InputConfig(**config_dict['input']),
            yolox=YOLOXConfig(**config_dict['yolox']),
            bytetrack=ByteTrackConfig(**config_dict['bytetrack']),
            output=OutputConfig(**config_dict['output']),
            display=DisplayConfig(**config_dict['display']),
            performance=PerformanceConfig(**config_dict['performance']),
            debug=DebugConfig(**config_dict['debug'])
        )
    
    def _resolve_paths(self, config: Config) -> None:
        """パス解決とディレクトリ作成"""
        import datetime
        
        # タイムスタンプ生成
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # パス内のタイムスタンプ置換
        config.output.video_path = config.output.video_path.replace('{timestamp}', timestamp)
        config.output.tracking_data_path = config.output.tracking_data_path.replace('{timestamp}', timestamp)
        config.output.frames_dir = config.output.frames_dir.replace('{timestamp}', timestamp)
        config.output.log_path = config.output.log_path.replace('{timestamp}', timestamp)
        
        # 出力ディレクトリ作成
        self._create_output_directories(config)
    
    def _create_output_directories(self, config: Config) -> None:
        """出力ディレクトリを作成"""
        directories = [
            config.output.output_dir,
            os.path.dirname(config.output.video_path),
            os.path.dirname(config.output.tracking_data_path),
            config.output.frames_dir,
            os.path.dirname(config.output.log_path)
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"ディレクトリ作成: {directory}")


def load_config(config_path: Union[str, Path]) -> Config:
    """設定ファイル読み込みのコンビニエンス関数"""
    loader = ConfigLoader()
    return loader.load_config(config_path)


if __name__ == "__main__":
    # テスト用コード
    try:
        config = load_config("config.yml")
        print("設定読み込み成功")
        print(f"入力タイプ: {config.input.type}")
        print(f"YOLOXモデル: {config.yolox.model_size}")
        print(f"出力ディレクトリ: {config.output.output_dir}")
    except Exception as e:
        print(f"エラー: {e}")