#!/usr/bin/env python3
"""
動画処理クラス
入力ソース処理と出力保存を統一管理
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union, Generator, Tuple
import logging
import time
import json
from datetime import datetime

from config_loader import Config, InputConfig, OutputConfig, DisplayConfig
from utils.video_utils import VideoCapture, create_video_writer, get_video_info, resize_frame
from utils.file_utils import ensure_dir, save_json
from utils.time_utils import FPSCounter, ProgressTracker, sleep_fps
from utils.visualization import ColorPalette, draw_tracks, draw_stats


class InputSourceProcessor:
    """入力ソース処理クラス"""
    
    def __init__(self, config: InputConfig, logger: Optional[logging.Logger] = None):
        """
        初期化
        
        Args:
            config: 入力設定
            logger: ロガー
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        self.cap = None
        self.source_info = None
        self.frame_count = 0
        self.fps_counter = FPSCounter()
        
        self._initialize()
    
    def _initialize(self):
        """初期化処理"""
        self.logger.info(f"入力ソース初期化: {self.config.type} - {self.config.source}")
        
        try:
            # 入力ソースに応じた処理
            if self.config.type == "webcam":
                self._setup_webcam()
            elif self.config.type == "video":
                self._setup_video()
            elif self.config.type == "rtsp":
                self._setup_rtsp()
            elif self.config.type in ["images", "image"]:
                self._setup_images()
            else:
                raise ValueError(f"サポートされていない入力タイプ: {self.config.type}")
            
            self.logger.info("入力ソース初期化完了")
            
        except Exception as e:
            self.logger.error(f"入力ソース初期化失敗: {e}")
            raise
    
    def _setup_webcam(self):
        """Webカメラ設定"""
        device_id = int(self.config.source)
        self.cap = VideoCapture(device_id, buffer_size=1)  # 低遅延
        
        # フレームレート設定
        if hasattr(self.cap.cap, 'set'):
            self.cap.cap.set(cv2.CAP_PROP_FPS, self.config.fps_limit)
        
        self.source_info = self.cap.info
        self.source_info['is_realtime'] = True
    
    def _setup_video(self):
        """動画ファイル設定"""
        video_path = Path(self.config.source)
        if not video_path.exists():
            raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
        
        self.cap = VideoCapture(str(video_path))
        self.source_info = self.cap.info
        self.source_info['is_realtime'] = False
    
    def _setup_rtsp(self):
        """RTSPストリーム設定"""
        self.cap = VideoCapture(self.config.source, buffer_size=1)
        self.source_info = self.cap.info
        self.source_info['is_realtime'] = True
    
    def _setup_images(self):
        """画像ディレクトリ設定"""
        # 画像処理は別途実装が必要
        raise NotImplementedError("画像入力は現在サポートされていません")
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        フレーム読み込み
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]: 成功フラグ, フレーム
        """
        if not self.cap:
            return False, None
        
        ret, frame = self.cap.read()
        
        if ret:
            self.frame_count += 1
            
            # フレーム前処理
            frame = self._preprocess_frame(frame)
            
            # FPS制限
            if self.config.fps_limit > 0 and not self.source_info.get('is_realtime', False):
                time.sleep(1.0 / self.config.fps_limit)
        
        return ret, frame
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """フレーム前処理"""
        # 解像度制限
        if self.config.max_width > 0 or self.config.max_height > 0:
            frame = resize_frame(
                frame,
                self.config.max_width,
                self.config.max_height,
                keep_aspect=True
            )
        
        return frame
    
    def get_progress(self) -> float:
        """進捗取得（0.0-1.0）"""
        if self.cap:
            return self.cap.get_progress()
        return 0.0
    
    def get_info(self) -> Dict[str, Any]:
        """ソース情報取得"""
        info = self.source_info.copy() if self.source_info else {}
        info.update({
            'frame_count': self.frame_count,
            'current_fps': self.fps_counter.get_fps(),
            'progress': self.get_progress()
        })
        return info
    
    def cleanup(self):
        """リソースクリーンアップ"""
        if self.cap:
            self.cap.release()
            self.cap = None
        self.logger.info("入力ソースクリーンアップ完了")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class OutputManager:
    """出力管理クラス"""
    
    def __init__(self, config: OutputConfig, input_info: Dict[str, Any], 
                 logger: Optional[logging.Logger] = None):
        """
        初期化
        
        Args:
            config: 出力設定
            input_info: 入力情報
            logger: ロガー
        """
        self.config = config
        self.input_info = input_info
        self.logger = logger or logging.getLogger(__name__)
        
        self.video_writer = None
        self.tracking_data = []
        self.frame_data = []
        
        self._initialize()
    
    def _initialize(self):
        """初期化処理"""
        # 出力ディレクトリ作成
        ensure_dir(self.config.output_dir)
        
        # 動画ライター初期化
        if self.config.save_video:
            self._setup_video_writer()
        
        # フレーム保存ディレクトリ
        if self.config.save_frames:
            ensure_dir(self.config.frames_dir)
        
        self.logger.info("出力管理初期化完了")
    
    def _setup_video_writer(self):
        """動画ライター設定"""
        try:
            output_path = Path(self.config.video_path)
            ensure_dir(output_path.parent)
            
            self.video_writer = create_video_writer(
                output_path,
                self.input_info['width'],
                self.input_info['height'],
                self.input_info.get('fps', 30),
                self.config.video_codec,
                self.config.video_quality
            )
            
            self.logger.info(f"動画ライター作成: {output_path}")
            
        except Exception as e:
            self.logger.error(f"動画ライター作成失敗: {e}")
            self.config.save_video = False
    
    def save_frame(self, frame: np.ndarray, frame_id: int, tracks: list):
        """
        フレーム保存
        
        Args:
            frame: フレーム
            frame_id: フレームID
            tracks: 追跡結果
        """
        # 動画保存
        if self.config.save_video and self.video_writer:
            try:
                self.video_writer.write(frame)
            except Exception as e:
                self.logger.error(f"動画フレーム保存失敗: {e}")
        
        # 個別フレーム保存
        if (self.config.save_frames and 
            frame_id % self.config.frame_interval == 0):
            self._save_individual_frame(frame, frame_id)
        
        # 追跡データ蓄積
        if self.config.save_tracking_data:
            self._accumulate_tracking_data(frame_id, tracks)
    
    def _save_individual_frame(self, frame: np.ndarray, frame_id: int):
        """個別フレーム保存"""
        try:
            frame_path = Path(self.config.frames_dir) / f"frame_{frame_id:06d}.jpg"
            cv2.imwrite(str(frame_path), frame)
        except Exception as e:
            self.logger.error(f"フレーム保存失敗: {e}")
    
    def _accumulate_tracking_data(self, frame_id: int, tracks: list):
        """追跡データ蓄積"""
        frame_data = {
            'frame_id': frame_id,
            'timestamp': time.time(),
            'tracks': []
        }
        
        for track in tracks:
            track_data = {
                'track_id': track['track_id'],
                'bbox': track['bbox'].tolist() if isinstance(track['bbox'], np.ndarray) else track['bbox'],
                'score': float(track['score']),
                'class_id': int(track['class_id']),
                'state': track.get('state', 'active')
            }
            frame_data['tracks'].append(track_data)
        
        self.tracking_data.append(frame_data)
    
    def finalize(self, final_statistics: Dict[str, Any]):
        """
        出力確定
        
        Args:
            final_statistics: 最終統計情報
        """
        # 動画ライター終了
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            self.logger.info(f"動画保存完了: {self.config.video_path}")
        
        # 追跡データ保存
        if self.config.save_tracking_data and self.tracking_data:
            self._save_tracking_data(final_statistics)
        
        self.logger.info("出力処理完了")
    
    def _save_tracking_data(self, statistics: Dict[str, Any]):
        """追跡データ保存"""
        try:
            tracking_export = {
                'metadata': {
                    'input_source': self.input_info,
                    'output_config': {
                        'save_video': self.config.save_video,
                        'video_path': self.config.video_path,
                        'save_tracking_data': self.config.save_tracking_data
                    },
                    'processing_timestamp': datetime.now().isoformat(),
                    'total_frames': len(self.tracking_data)
                },
                'statistics': statistics,
                'tracking_data': self.tracking_data
            }
            
            save_json(tracking_export, self.config.tracking_data_path)
            self.logger.info(f"追跡データ保存完了: {self.config.tracking_data_path}")
            
        except Exception as e:
            self.logger.error(f"追跡データ保存失敗: {e}")


class VideoProcessor:
    """動画処理統合クラス"""
    
    def __init__(self, config: Config, logger: Optional[logging.Logger] = None):
        """
        初期化
        
        Args:
            config: 全体設定
            logger: ロガー
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        self.input_processor = None
        self.output_manager = None
        self.color_palette = None
        self.fps_counter = FPSCounter()
        self.progress_tracker = None
        
        # 統計情報
        self.processing_stats = {
            'start_time': None,
            'end_time': None,
            'total_frames': 0,
            'processing_fps': 0,
            'avg_detection_time': 0,
            'avg_tracking_time': 0,
            'avg_total_time': 0
        }
    
    def initialize(self):
        """初期化処理"""
        self.logger.info("動画処理初期化開始")
        
        # 入力処理器初期化
        self.input_processor = InputSourceProcessor(self.config.input, self.logger)
        
        # 出力管理器初期化
        input_info = self.input_processor.get_info()
        self.output_manager = OutputManager(self.config.output, input_info, self.logger)
        
        # 可視化設定
        self.color_palette = ColorPalette(
            self.config.display.color_palette,
            num_colors=50
        )
        
        # 進捗追跡
        total_frames = input_info.get('total_frames', 0)
        if total_frames > 0:
            self.progress_tracker = ProgressTracker(total_frames, "動画処理")
        
        self.processing_stats['start_time'] = time.time()
        self.logger.info("動画処理初期化完了")
    
    def process_frames(self) -> Generator[Tuple[np.ndarray, Dict[str, Any]], None, None]:
        """
        フレーム処理ジェネレータ
        
        Yields:
            Tuple[np.ndarray, Dict]: 処理済みフレーム, メタデータ
        """
        frame_id = 0
        last_time = time.time()
        
        while True:
            # フレーム読み込み
            ret, frame = self.input_processor.read_frame()
            if not ret:
                break
            
            frame_id += 1
            current_time = time.time()
            
            # FPS制限適用
            if self.config.input.fps_limit > 0:
                last_time = sleep_fps(self.config.input.fps_limit, last_time)
            
            # FPS更新
            processing_fps = self.fps_counter.update()
            
            # 進捗更新
            progress_info = {}
            if self.progress_tracker:
                progress_info = self.progress_tracker.update()
            
            # メタデータ作成
            metadata = {
                'frame_id': frame_id,
                'timestamp': current_time,
                'processing_fps': processing_fps,
                'input_info': self.input_processor.get_info(),
                'progress': progress_info
            }
            
            yield frame, metadata
    
    def save_result(self, frame: np.ndarray, tracks: list, metadata: Dict[str, Any]):
        """
        結果保存
        
        Args:
            frame: 処理済みフレーム
            tracks: 追跡結果
            metadata: メタデータ
        """
        self.output_manager.save_frame(frame, metadata['frame_id'], tracks)
        self.processing_stats['total_frames'] += 1
    
    def render_frame(self, frame: np.ndarray, tracks: list, 
                    detection_stats: Dict[str, Any]) -> np.ndarray:
        """
        フレーム描画
        
        Args:
            frame: 入力フレーム
            tracks: 追跡結果
            detection_stats: 検出統計
            
        Returns:
            np.ndarray: 描画済みフレーム
        """
        result_frame = frame.copy()
        
        # 追跡結果描画
        if tracks:
            result_frame = draw_tracks(
                result_frame,
                tracks,
                self.color_palette,
                draw_boxes=self.config.display.draw_boxes,
                draw_ids=self.config.display.draw_track_ids,
                draw_trails=self.config.display.draw_trails,
                trail_length=self.config.display.trail_length,
                thickness=self.config.display.box_thickness,
                id_font_size=self.config.display.id_font_size
            )
        
        # 統計情報描画
        if self.config.display.show_stats:
            stats = {
                'Tracks': len(tracks),
                'FPS': detection_stats.get('processing_fps', 0),
                'Detection': f"{detection_stats.get('inference_time', 0)*1000:.1f}ms",
                'Tracking': f"{detection_stats.get('tracking_time', 0)*1000:.1f}ms"
            }
            
            result_frame = draw_stats(result_frame, stats)
        
        return result_frame
    
    def display_frame(self, frame: np.ndarray) -> bool:
        """
        フレーム表示
        
        Args:
            frame: 表示フレーム
            
        Returns:
            bool: 継続フラグ（Falseで終了）
        """
        if not self.config.display.show_realtime:
            return True
        
        # ウィンドウサイズ調整
        display_frame = resize_frame(
            frame,
            self.config.display.window_width,
            self.config.display.window_height,
            keep_aspect=True
        )
        
        cv2.imshow('YOLOX + ByteTrack', display_frame)
        
        # キー入力チェック
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            return False
        elif key == ord(' '):  # スペースでポーズ
            cv2.waitKey(0)
        
        return True
    
    def finalize(self, final_tracking_stats: Dict[str, Any]):
        """
        処理終了
        
        Args:
            final_tracking_stats: 最終追跡統計
        """
        self.processing_stats['end_time'] = time.time()
        
        # 統計計算
        total_time = self.processing_stats['end_time'] - self.processing_stats['start_time']
        if total_time > 0:
            self.processing_stats['processing_fps'] = self.processing_stats['total_frames'] / total_time
        
        # 統合統計
        integrated_stats = {
            **self.processing_stats,
            **final_tracking_stats,
            'input_info': self.input_processor.get_info() if self.input_processor else {},
        }
        
        # 出力確定
        if self.output_manager:
            self.output_manager.finalize(integrated_stats)
        
        self.logger.info(f"動画処理完了 - 総フレーム数: {self.processing_stats['total_frames']}, "
                        f"処理時間: {total_time:.2f}秒, "
                        f"平均FPS: {self.processing_stats['processing_fps']:.2f}")
    
    def cleanup(self):
        """リソースクリーンアップ"""
        if self.input_processor:
            self.input_processor.cleanup()
        
        if self.config.display.show_realtime:
            cv2.destroyAllWindows()
        
        self.logger.info("動画処理クリーンアップ完了")
    
    def __enter__(self):
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()