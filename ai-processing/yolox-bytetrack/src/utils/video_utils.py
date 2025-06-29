#!/usr/bin/env python3
"""
動画処理ユーティリティ
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Union, Dict, Any
import logging


def get_video_info(source: Union[str, int]) -> Dict[str, Any]:
    """
    動画ソースの情報を取得
    
    Args:
        source: 動画ソース（ファイルパス、カメラID、URL）
        
    Returns:
        Dict: 動画情報
    """
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        raise RuntimeError(f"動画ソースを開けません: {source}")
    
    info = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'fourcc': int(cap.get(cv2.CAP_PROP_FOURCC)),
        'is_camera': isinstance(source, int) or str(source).startswith(('rtsp://', 'http://')),
        'source': source
    }
    
    cap.release()
    return info


def create_video_writer(output_path: Union[str, Path], 
                       width: int, 
                       height: int, 
                       fps: float,
                       codec: str = 'mp4v',
                       quality: int = 90) -> cv2.VideoWriter:
    """
    動画ライターを作成
    
    Args:
        output_path: 出力パス
        width: 幅
        height: 高さ
        fps: FPS
        codec: コーデック
        quality: 品質（0-100）
        
    Returns:
        cv2.VideoWriter: 動画ライター
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # コーデック設定
    fourcc_map = {
        'mp4v': cv2.VideoWriter_fourcc(*'mp4v'),
        'XVID': cv2.VideoWriter_fourcc(*'XVID'),
        'H264': cv2.VideoWriter_fourcc(*'H264'),
        'MJPG': cv2.VideoWriter_fourcc(*'MJPG')
    }
    
    fourcc = fourcc_map.get(codec, cv2.VideoWriter_fourcc(*'mp4v'))
    
    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        fps,
        (width, height)
    )
    
    if not writer.isOpened():
        raise RuntimeError(f"動画ライターの作成に失敗: {output_path}")
    
    return writer


def resize_frame(frame: np.ndarray, 
                max_width: int = 0, 
                max_height: int = 0,
                keep_aspect: bool = True) -> np.ndarray:
    """
    フレームをリサイズ
    
    Args:
        frame: 入力フレーム
        max_width: 最大幅（0で制限なし）
        max_height: 最大高さ（0で制限なし）
        keep_aspect: アスペクト比維持
        
    Returns:
        np.ndarray: リサイズ後フレーム
    """
    if max_width <= 0 and max_height <= 0:
        return frame
    
    h, w = frame.shape[:2]
    
    if keep_aspect:
        # アスペクト比を維持してリサイズ
        scale_w = max_width / w if max_width > 0 else float('inf')
        scale_h = max_height / h if max_height > 0 else float('inf')
        scale = min(scale_w, scale_h, 1.0)  # 拡大はしない
        
        new_w = int(w * scale)
        new_h = int(h * scale)
    else:
        # 指定サイズに強制リサイズ
        new_w = max_width if max_width > 0 else w
        new_h = max_height if max_height > 0 else h
    
    if (new_w, new_h) == (w, h):
        return frame
    
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)


def preprocess_frame(frame: np.ndarray, 
                    target_size: Tuple[int, int],
                    normalize: bool = True,
                    swap_rb: bool = True) -> Tuple[np.ndarray, float]:
    """
    YOLOX用フレーム前処理
    
    Args:
        frame: 入力フレーム (BGR)
        target_size: 目標サイズ (width, height)
        normalize: 正規化の有無
        swap_rb: RGB変換の有無
        
    Returns:
        Tuple[np.ndarray, float]: 前処理済みフレーム, スケール比
    """
    # アスペクト比を維持してリサイズ
    h, w = frame.shape[:2]
    target_w, target_h = target_size
    
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    
    # リサイズ
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    # パディング
    padded = np.full((target_h, target_w, 3), 114, dtype=np.uint8)
    top = (target_h - new_h) // 2
    left = (target_w - new_w) // 2
    padded[top:top+new_h, left:left+new_w] = resized
    
    # RGB変換
    if swap_rb:
        padded = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
    
    # 正規化
    if normalize:
        padded = padded.astype(np.float32) / 255.0
    
    return padded, scale


def postprocess_boxes(boxes: np.ndarray, 
                     scale: float, 
                     input_size: Tuple[int, int],
                     original_size: Tuple[int, int]) -> np.ndarray:
    """
    検出ボックスの後処理（座標変換）
    
    Args:
        boxes: 検出ボックス [N, 4] (x1, y1, x2, y2)
        scale: スケール比
        input_size: 入力サイズ (width, height)
        original_size: 元画像サイズ (width, height)
        
    Returns:
        np.ndarray: 変換後ボックス
    """
    if len(boxes) == 0:
        return boxes
    
    input_w, input_h = input_size
    orig_w, orig_h = original_size
    
    # パディングオフセット計算
    new_w, new_h = int(orig_w * scale), int(orig_h * scale)
    pad_x = (input_w - new_w) // 2
    pad_y = (input_h - new_h) // 2
    
    # パディング除去
    boxes[:, [0, 2]] -= pad_x
    boxes[:, [1, 3]] -= pad_y
    
    # スケール戻し
    boxes[:, [0, 2]] /= scale
    boxes[:, [1, 3]] /= scale
    
    # クリッピング
    boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, orig_w)
    boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, orig_h)
    
    return boxes


class VideoCapture:
    """拡張VideoCapture クラス"""
    
    def __init__(self, source: Union[str, int], buffer_size: int = 1):
        self.source = source
        self.cap = cv2.VideoCapture(source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"動画ソースを開けません: {source}")
        
        # バッファサイズ設定（リアルタイム用）
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
        
        self.info = self._get_info()
        self.frame_count = 0
    
    def _get_info(self) -> Dict[str, Any]:
        """動画情報取得"""
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'total_frames': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fourcc': int(self.cap.get(cv2.CAP_PROP_FOURCC))
        }
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """フレーム読み込み"""
        ret, frame = self.cap.read()
        if ret:
            self.frame_count += 1
        return ret, frame
    
    def get_progress(self) -> float:
        """進捗率取得（0.0-1.0）"""
        if self.info['total_frames'] <= 0:
            return 0.0
        return min(1.0, self.frame_count / self.info['total_frames'])
    
    def seek(self, frame_number: int) -> bool:
        """フレーム位置設定"""
        success = self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        if success:
            self.frame_count = frame_number
        return success
    
    def release(self):
        """リソース解放"""
        if self.cap:
            self.cap.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def extract_frames(video_path: Union[str, Path], 
                  output_dir: Union[str, Path],
                  interval: int = 30,
                  max_frames: int = 0) -> int:
    """
    動画からフレームを抽出
    
    Args:
        video_path: 動画ファイルパス
        output_dir: 出力ディレクトリ
        interval: 抽出間隔（フレーム数）
        max_frames: 最大抽出フレーム数（0で制限なし）
        
    Returns:
        int: 抽出されたフレーム数
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_count = 0
    
    with VideoCapture(str(video_path)) as cap:
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 指定間隔でフレーム抽出
            if frame_idx % interval == 0:
                output_path = output_dir / f"frame_{frame_idx:06d}.jpg"
                cv2.imwrite(str(output_path), frame)
                extracted_count += 1
                
                # 最大フレーム数チェック
                if max_frames > 0 and extracted_count >= max_frames:
                    break
            
            frame_idx += 1
    
    return extracted_count