#!/usr/bin/env python3
"""
ByteTrackラッパークラス
ByteTrack物体追跡の統一インターフェースを提供
"""

import sys
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
import time
from collections import defaultdict, deque

# ByteTrack関連インポート
sys.path.append('/workspace/ByteTrack')
from bytetrack_yolox.tracker.byte_tracker import BYTETracker
from bytetrack_yolox.tracking_utils.timer import Timer

from config_loader import ByteTrackConfig


class Track:
    """追跡オブジェクトクラス"""
    
    def __init__(self, track_id: int, bbox: np.ndarray, score: float, class_id: int, frame_id: int):
        """
        初期化
        
        Args:
            track_id: 追跡ID
            bbox: バウンディングボックス [x1, y1, x2, y2]
            score: 信頼度スコア
            class_id: クラスID
            frame_id: フレームID
        """
        self.track_id = track_id
        self.bbox = bbox.copy()
        self.score = score
        self.class_id = class_id
        self.start_frame = frame_id
        self.last_frame = frame_id
        self.age = 1
        self.hits = 1
        self.time_since_update = 0
        
        # 履歴管理
        self.history = deque(maxlen=100)  # 最大100フレーム
        self.history.append(self._get_center())
        
        # 統計情報
        self.max_score = score
        self.avg_score = score
        self.total_score = score
        
        # 状態
        self.is_activated = True
        self.state = 'active'  # 'active', 'lost', 'removed'
    
    def _get_center(self) -> Tuple[float, float]:
        """中心座標取得"""
        return ((self.bbox[0] + self.bbox[2]) / 2, (self.bbox[1] + self.bbox[3]) / 2)
    
    def update(self, bbox: np.ndarray, score: float, frame_id: int):
        """
        追跡更新
        
        Args:
            bbox: 新しいバウンディングボックス
            score: 新しい信頼度スコア
            frame_id: フレームID
        """
        self.bbox = bbox.copy()
        self.score = score
        self.last_frame = frame_id
        self.age = frame_id - self.start_frame + 1
        self.hits += 1
        self.time_since_update = 0
        
        # 履歴更新
        self.history.append(self._get_center())
        
        # 統計更新
        self.max_score = max(self.max_score, score)
        self.total_score += score
        self.avg_score = self.total_score / self.hits
        
        self.state = 'active'
    
    def predict(self):
        """状態予測（簡易版）"""
        self.time_since_update += 1
        if self.time_since_update > 1:
            self.state = 'lost'
    
    def mark_removed(self):
        """削除マーク"""
        self.state = 'removed'
        self.is_activated = False
    
    def get_info(self) -> Dict[str, Any]:
        """追跡情報取得"""
        return {
            'track_id': self.track_id,
            'bbox': self.bbox,
            'score': self.score,
            'class_id': self.class_id,
            'age': self.age,
            'hits': self.hits,
            'start_frame': self.start_frame,
            'last_frame': self.last_frame,
            'time_since_update': self.time_since_update,
            'max_score': self.max_score,
            'avg_score': self.avg_score,
            'state': self.state,
            'history': list(self.history),
            'track_length': len(self.history)
        }


class ByteTrackWrapper:
    """ByteTrack追跡器ラッパークラス"""
    
    def __init__(self, config: ByteTrackConfig, logger: Optional[logging.Logger] = None):
        """
        初期化
        
        Args:
            config: ByteTrack設定
            logger: ロガー
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # ByteTracker初期化
        self.tracker = None
        self.frame_id = 0
        
        # 追跡管理
        self.active_tracks = {}  # track_id -> Track
        self.completed_tracks = {}  # track_id -> Track
        self.track_history = defaultdict(list)  # track_id -> [Track info]
        
        # 統計情報
        self.stats = {
            'total_detections': 0,
            'total_tracks': 0,
            'active_track_count': 0,
            'completed_track_count': 0,
            'avg_track_length': 0,
            'max_track_length': 0,
            'frames_processed': 0
        }
        
        self._initialize()
    
    def _initialize(self):
        """初期化処理"""
        self.logger.info("ByteTrack初期化開始")
        
        try:
            # ByteTrackerの引数を作成
            class Args:
                def __init__(self, config: ByteTrackConfig):
                    self.track_thresh = config.track_thresh
                    self.track_buffer = config.track_buffer
                    self.match_thresh = config.match_thresh
                    self.aspect_ratio_thresh = 1.6
                    self.min_box_area = 10
                    self.mot20 = False
            
            args = Args(self.config)
            self.tracker = BYTETracker(args, frame_rate=self.config.frame_rate)
            
            self.logger.info("ByteTracker初期化完了")
            self.logger.info(f"設定 - track_thresh: {self.config.track_thresh}, "
                           f"match_thresh: {self.config.match_thresh}, "
                           f"track_buffer: {self.config.track_buffer}")
            
        except Exception as e:
            self.logger.error(f"ByteTracker初期化失敗: {e}")
            raise RuntimeError(f"ByteTracker初期化失敗: {e}")
    
    def update(self, detections: Dict[str, np.ndarray]) -> List[Dict[str, Any]]:
        """
        追跡更新
        
        Args:
            detections: YOLOX検出結果 {
                'boxes': np.ndarray [N, 4],
                'scores': np.ndarray [N],
                'class_ids': np.ndarray [N]
            }
            
        Returns:
            List[Dict]: 追跡結果リスト
        """
        start_time = time.time()
        self.frame_id += 1
        
        # 検出結果をByteTracker形式に変換
        byte_detections = self._convert_detections(detections)
        
        # 追跡更新
        try:
            online_targets = self.tracker.update(byte_detections, None, None)
            tracking_time = time.time() - start_time
            
            # 結果変換
            tracks = self._convert_tracks(online_targets, tracking_time)
            
            # 追跡管理更新
            self._update_track_management(tracks)
            
            # 統計更新
            self._update_statistics(detections, tracks)
            
            self.logger.debug(f"Frame {self.frame_id}: {len(detections['boxes'])} 検出, "
                            f"{len(tracks)} 追跡, 処理時間: {tracking_time*1000:.1f}ms")
            
            return tracks
            
        except Exception as e:
            self.logger.error(f"追跡更新失敗 (Frame {self.frame_id}): {e}")
            return []
    
    def _convert_detections(self, detections: Dict[str, np.ndarray]) -> np.ndarray:
        """
        YOLOX検出結果をByteTracker形式に変換
        
        Args:
            detections: YOLOX検出結果
            
        Returns:
            np.ndarray: ByteTracker形式 [N, 6] (x1, y1, x2, y2, score, class_id)
        """
        boxes = detections['boxes']
        scores = detections['scores']
        class_ids = detections['class_ids']
        
        if len(boxes) == 0:
            return np.empty((0, 6))
        
        # [x1, y1, x2, y2, score, class_id] 形式に変換
        byte_detections = np.column_stack([
            boxes,
            scores,
            class_ids
        ])
        
        return byte_detections
    
    def _convert_tracks(self, online_targets, tracking_time: float) -> List[Dict[str, Any]]:
        """
        ByteTracker結果を統一形式に変換
        
        Args:
            online_targets: ByteTracker追跡結果
            tracking_time: 追跡処理時間
            
        Returns:
            List[Dict]: 変換後追跡結果
        """
        tracks = []
        
        for target in online_targets:
            # バウンディングボックス取得
            bbox = target.tlbr  # [x1, y1, x2, y2]
            
            track_info = {
                'track_id': target.track_id,
                'bbox': bbox,
                'score': target.score,
                'class_id': getattr(target, 'class_id', 0),
                'frame_id': self.frame_id,
                'tracking_time': tracking_time,
                'state': 'active',
                'age': getattr(target, 'age', 1),
                'hits': getattr(target, 'hits', 1),
                'time_since_update': getattr(target, 'time_since_update', 0)
            }
            
            # 履歴情報追加（利用可能な場合）
            if hasattr(target, 'history'):
                track_info['history'] = target.history
            else:
                # 中心座標から簡易履歴作成
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
                track_info['history'] = [(center_x, center_y)]
            
            tracks.append(track_info)
        
        return tracks
    
    def _update_track_management(self, tracks: List[Dict[str, Any]]):
        """追跡管理更新"""
        current_track_ids = set()
        
        # アクティブ追跡更新
        for track_info in tracks:
            track_id = track_info['track_id']
            current_track_ids.add(track_id)
            
            if track_id in self.active_tracks:
                # 既存追跡更新
                self.active_tracks[track_id].update(
                    track_info['bbox'],
                    track_info['score'],
                    self.frame_id
                )
            else:
                # 新規追跡作成
                new_track = Track(
                    track_id,
                    track_info['bbox'],
                    track_info['score'],
                    track_info['class_id'],
                    self.frame_id
                )
                self.active_tracks[track_id] = new_track
                
                self.logger.debug(f"新規追跡開始: ID {track_id}")
        
        # 非アクティブ追跡処理
        inactive_tracks = []
        for track_id, track in self.active_tracks.items():
            if track_id not in current_track_ids:
                track.predict()
                
                # 削除条件チェック
                if (track.time_since_update > self.config.track_buffer or
                    track.age < self.config.min_track_length):
                    inactive_tracks.append(track_id)
        
        # 完了追跡への移動
        for track_id in inactive_tracks:
            track = self.active_tracks[track_id]
            track.mark_removed()
            
            # 最小追跡長を満たす場合のみ完了リストに追加
            if track.age >= self.config.min_track_length:
                self.completed_tracks[track_id] = track
                self.track_history[track_id] = track.get_info()
                
                self.logger.debug(f"追跡完了: ID {track_id}, 長さ: {track.age}")
            else:
                self.logger.debug(f"追跡削除: ID {track_id}, 長さ: {track.age} (短すぎる)")
            
            del self.active_tracks[track_id]
    
    def _update_statistics(self, detections: Dict[str, np.ndarray], tracks: List[Dict[str, Any]]):
        """統計情報更新"""
        self.stats['frames_processed'] += 1
        self.stats['total_detections'] += len(detections['boxes'])
        self.stats['active_track_count'] = len(self.active_tracks)
        self.stats['completed_track_count'] = len(self.completed_tracks)
        self.stats['total_tracks'] = len(self.active_tracks) + len(self.completed_tracks)
        
        # 平均追跡長計算
        if self.completed_tracks:
            total_length = sum(track.age for track in self.completed_tracks.values())
            self.stats['avg_track_length'] = total_length / len(self.completed_tracks)
            self.stats['max_track_length'] = max(track.age for track in self.completed_tracks.values())
    
    def get_active_tracks(self) -> List[Dict[str, Any]]:
        """
        アクティブ追跡取得
        
        Returns:
            List[Dict]: アクティブ追跡リスト
        """
        return [track.get_info() for track in self.active_tracks.values()]
    
    def get_completed_tracks(self) -> List[Dict[str, Any]]:
        """
        完了追跡取得
        
        Returns:
            List[Dict]: 完了追跡リスト
        """
        return [track.get_info() for track in self.completed_tracks.values()]
    
    def get_track_by_id(self, track_id: int) -> Optional[Dict[str, Any]]:
        """
        ID指定追跡取得
        
        Args:
            track_id: 追跡ID
            
        Returns:
            Optional[Dict]: 追跡情報（存在しない場合はNone）
        """
        if track_id in self.active_tracks:
            return self.active_tracks[track_id].get_info()
        elif track_id in self.completed_tracks:
            return self.completed_tracks[track_id].get_info()
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        統計情報取得
        
        Returns:
            Dict: 統計情報
        """
        stats = self.stats.copy()
        
        # 追加統計計算
        if stats['frames_processed'] > 0:
            stats['avg_detections_per_frame'] = stats['total_detections'] / stats['frames_processed']
            stats['avg_active_tracks_per_frame'] = stats['active_track_count']
        
        return stats
    
    def export_tracking_data(self) -> Dict[str, Any]:
        """
        追跡データエクスポート
        
        Returns:
            Dict: 全追跡データ
        """
        return {
            'active_tracks': [track.get_info() for track in self.active_tracks.values()],
            'completed_tracks': [track.get_info() for track in self.completed_tracks.values()],
            'track_history': dict(self.track_history),
            'statistics': self.get_statistics(),
            'config': {
                'track_thresh': self.config.track_thresh,
                'match_thresh': self.config.match_thresh,
                'track_buffer': self.config.track_buffer,
                'frame_rate': self.config.frame_rate,
                'min_track_length': self.config.min_track_length
            },
            'metadata': {
                'total_frames': self.frame_id,
                'export_timestamp': time.time()
            }
        }
    
    def reset(self):
        """追跡器リセット"""
        self.frame_id = 0
        self.active_tracks.clear()
        self.completed_tracks.clear()
        self.track_history.clear()
        
        # 統計リセット
        self.stats = {
            'total_detections': 0,
            'total_tracks': 0,
            'active_track_count': 0,
            'completed_track_count': 0,
            'avg_track_length': 0,
            'max_track_length': 0,
            'frames_processed': 0
        }
        
        # ByteTracker再初期化
        self._initialize()
        
        self.logger.info("ByteTracker リセット完了")
    
    def get_tracker_info(self) -> Dict[str, Any]:
        """
        追跡器情報取得
        
        Returns:
            Dict: 追跡器情報
        """
        return {
            'config': {
                'track_thresh': self.config.track_thresh,
                'high_thresh': self.config.high_thresh,
                'match_thresh': self.config.match_thresh,
                'track_buffer': self.config.track_buffer,
                'frame_rate': self.config.frame_rate,
                'min_track_length': self.config.min_track_length
            },
            'state': {
                'frame_id': self.frame_id,
                'active_tracks': len(self.active_tracks),
                'completed_tracks': len(self.completed_tracks)
            },
            'performance': self.get_statistics()
        }
    
    def cleanup(self):
        """リソースクリーンアップ"""
        if hasattr(self, 'tracker') and self.tracker is not None:
            del self.tracker
        
        self.active_tracks.clear()
        self.completed_tracks.clear()
        self.track_history.clear()
        
        self.logger.info("ByteTrack リソースクリーンアップ完了")
    
    def __del__(self):
        """デストラクタ"""
        self.cleanup()