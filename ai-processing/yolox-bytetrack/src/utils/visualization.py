#!/usr/bin/env python3
"""
可視化ユーティリティ
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import colorsys


def generate_colors(num_colors: int, seed: int = 42) -> List[Tuple[int, int, int]]:
    """
    視認性の良いカラーパレットを生成
    
    Args:
        num_colors: 生成する色数
        seed: ランダムシード
        
    Returns:
        List[Tuple[int, int, int]]: BGR色のリスト
    """
    np.random.seed(seed)
    colors = []
    
    for i in range(num_colors):
        # HSV色空間で均等に分散した色を生成
        hue = i / num_colors
        saturation = 0.7 + 0.3 * np.random.random()  # 0.7-1.0
        value = 0.8 + 0.2 * np.random.random()       # 0.8-1.0
        
        # HSV → RGB → BGR変換
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        bgr = (int(rgb[2] * 255), int(rgb[1] * 255), int(rgb[0] * 255))
        colors.append(bgr)
    
    return colors


class ColorPalette:
    """カラーパレット管理クラス"""
    
    def __init__(self, palette_type: str = "auto", num_colors: int = 100):
        self.palette_type = palette_type
        self.colors = self._generate_palette(num_colors)
    
    def _generate_palette(self, num_colors: int) -> List[Tuple[int, int, int]]:
        """パレット生成"""
        if self.palette_type == "fixed":
            # 固定カラーセット
            base_colors = [
                (255, 0, 0),    # 青
                (0, 255, 0),    # 緑
                (0, 0, 255),    # 赤
                (255, 255, 0),  # シアン
                (255, 0, 255),  # マゼンタ
                (0, 255, 255),  # 黄
                (128, 0, 0),    # ダークブルー
                (0, 128, 0),    # ダークグリーン
                (0, 0, 128),    # ダークレッド
                (128, 128, 0),  # ダークシアン
            ]
            # 不足分は繰り返し
            return (base_colors * ((num_colors // len(base_colors)) + 1))[:num_colors]
        
        elif self.palette_type == "rainbow":
            # レインボーカラー
            colors = []
            for i in range(num_colors):
                hue = i / num_colors
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                bgr = (int(rgb[2] * 255), int(rgb[1] * 255), int(rgb[0] * 255))
                colors.append(bgr)
            return colors
        
        else:  # "auto"
            return generate_colors(num_colors)
    
    def get_color(self, track_id: int) -> Tuple[int, int, int]:
        """
        トラックIDに対応する色を取得
        
        Args:
            track_id: トラックID
            
        Returns:
            Tuple[int, int, int]: BGR色
        """
        return self.colors[track_id % len(self.colors)]


def draw_boxes(frame: np.ndarray,
               boxes: np.ndarray,
               scores: Optional[np.ndarray] = None,
               class_ids: Optional[np.ndarray] = None,
               class_names: Optional[List[str]] = None,
               colors: Optional[List[Tuple[int, int, int]]] = None,
               thickness: int = 2) -> np.ndarray:
    """
    検出ボックスを描画
    
    Args:
        frame: 入力フレーム
        boxes: ボックス座標 [N, 4] (x1, y1, x2, y2)
        scores: 信頼度スコア [N]
        class_ids: クラスID [N]
        class_names: クラス名リスト
        colors: 色リスト
        thickness: 線の太さ
        
    Returns:
        np.ndarray: 描画後フレーム
    """
    if len(boxes) == 0:
        return frame
    
    result = frame.copy()
    
    # デフォルト色設定
    if colors is None:
        colors = generate_colors(len(boxes))
    
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box.astype(int)
        
        # 色選択
        if class_ids is not None and len(colors) > 1:
            color = colors[int(class_ids[i]) % len(colors)]
        else:
            color = colors[i % len(colors)]
        
        # ボックス描画
        cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness)
        
        # ラベル作成
        label_parts = []
        if class_names is not None and class_ids is not None:
            class_name = class_names[int(class_ids[i])] if int(class_ids[i]) < len(class_names) else f"class_{int(class_ids[i])}"
            label_parts.append(class_name)
        
        if scores is not None:
            label_parts.append(f"{scores[i]:.2f}")
        
        if label_parts:
            label = " ".join(label_parts)
            
            # ラベル背景
            (label_w, label_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(result, (x1, y1 - label_h - baseline), (x1 + label_w, y1), color, -1)
            
            # ラベルテキスト
            cv2.putText(result, label, (x1, y1 - baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return result


def draw_tracks(frame: np.ndarray,
               tracks: List[Dict[str, Any]],
               color_palette: ColorPalette,
               draw_boxes: bool = True,
               draw_ids: bool = True,
               draw_trails: bool = True,
               trail_length: int = 30,
               thickness: int = 2,
               id_font_size: float = 0.8) -> np.ndarray:
    """
    追跡結果を描画
    
    Args:
        frame: 入力フレーム
        tracks: 追跡結果リスト
        color_palette: カラーパレット
        draw_boxes: ボックス描画
        draw_ids: ID描画
        draw_trails: 軌跡描画
        trail_length: 軌跡長
        thickness: 線の太さ
        id_font_size: IDフォントサイズ
        
    Returns:
        np.ndarray: 描画後フレーム
    """
    if not tracks:
        return frame
    
    result = frame.copy()
    
    for track in tracks:
        track_id = track['track_id']
        bbox = track['bbox']  # [x1, y1, x2, y2]
        color = color_palette.get_color(track_id)
        
        x1, y1, x2, y2 = bbox.astype(int)
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        
        # ボックス描画
        if draw_boxes:
            cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness)
        
        # ID描画
        if draw_ids:
            id_text = f"ID:{track_id}"
            font_scale = id_font_size
            font_thickness = max(1, int(thickness * 0.8))
            
            (text_w, text_h), baseline = cv2.getTextSize(id_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            
            # ID背景
            cv2.rectangle(result, (x1, y1 - text_h - baseline - 5), (x1 + text_w + 5, y1), color, -1)
            
            # IDテキスト
            cv2.putText(result, id_text, (x1 + 2, y1 - baseline - 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
        
        # 軌跡描画
        if draw_trails and 'history' in track and len(track['history']) > 1:
            history = track['history'][-trail_length:]  # 最新N個
            
            # 軌跡線描画
            for i in range(1, len(history)):
                pt1 = (int(history[i-1][0]), int(history[i-1][1]))
                pt2 = (int(history[i][0]), int(history[i][1]))
                
                # 古い軌跡ほど薄く
                alpha = i / len(history)
                trail_color = tuple(int(c * alpha) for c in color)
                trail_thickness = max(1, int(thickness * alpha))
                
                cv2.line(result, pt1, pt2, trail_color, trail_thickness)
            
            # 現在位置を強調
            cv2.circle(result, (center_x, center_y), thickness + 1, color, -1)
    
    return result


def draw_stats(frame: np.ndarray,
              stats: Dict[str, Any],
              position: Tuple[int, int] = (10, 30),
              font_scale: float = 0.7,
              color: Tuple[int, int, int] = (255, 255, 255),
              bg_color: Tuple[int, int, int] = (0, 0, 0),
              thickness: int = 1) -> np.ndarray:
    """
    統計情報を描画
    
    Args:
        frame: 入力フレーム
        stats: 統計情報辞書
        position: 描画位置 (x, y)
        font_scale: フォントスケール
        color: テキスト色
        bg_color: 背景色
        thickness: 線の太さ
        
    Returns:
        np.ndarray: 描画後フレーム
    """
    result = frame.copy()
    x, y = position
    line_height = int(25 * font_scale)
    
    # 統計情報テキスト作成
    lines = []
    for key, value in stats.items():
        if isinstance(value, float):
            if 'fps' in key.lower():
                lines.append(f"{key}: {value:.1f}")
            elif 'time' in key.lower():
                lines.append(f"{key}: {value*1000:.1f}ms")
            else:
                lines.append(f"{key}: {value:.2f}")
        else:
            lines.append(f"{key}: {value}")
    
    # 背景描画
    if lines:
        max_width = 0
        total_height = len(lines) * line_height + 10
        
        for line in lines:
            (text_w, text_h), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            max_width = max(max_width, text_w)
        
        # 半透明背景
        overlay = result.copy()
        cv2.rectangle(overlay, (x - 5, y - line_height), 
                     (x + max_width + 10, y + total_height - line_height), bg_color, -1)
        cv2.addWeighted(overlay, 0.7, result, 0.3, 0, result)
    
    # テキスト描画
    for i, line in enumerate(lines):
        text_y = y + i * line_height
        cv2.putText(result, line, (x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                   font_scale, color, thickness)
    
    return result


def create_detection_summary_image(detections: List[Dict[str, Any]], 
                                 frame_shape: Tuple[int, int],
                                 class_names: Optional[List[str]] = None) -> np.ndarray:
    """
    検出結果のサマリー画像を作成
    
    Args:
        detections: 検出結果リスト
        frame_shape: フレーム形状 (height, width)
        class_names: クラス名リスト
        
    Returns:
        np.ndarray: サマリー画像
    """
    h, w = frame_shape
    summary_img = np.zeros((h, w, 3), dtype=np.uint8)
    
    if not detections:
        # 検出なしメッセージ
        text = "No detections"
        font_scale = 1.0
        thickness = 2
        (text_w, text_h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        
        x = (w - text_w) // 2
        y = (h + text_h) // 2
        cv2.putText(summary_img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                   font_scale, (128, 128, 128), thickness)
        return summary_img
    
    # 検出数によって配置を決定
    num_detections = len(detections)
    cols = int(np.ceil(np.sqrt(num_detections)))
    rows = int(np.ceil(num_detections / cols))
    
    cell_w = w // cols
    cell_h = h // rows
    
    colors = generate_colors(num_detections)
    
    for i, detection in enumerate(detections):
        row = i // cols
        col = i % cols
        
        x1 = col * cell_w
        y1 = row * cell_h
        x2 = x1 + cell_w
        y2 = y1 + cell_h
        
        color = colors[i]
        
        # セル境界描画
        cv2.rectangle(summary_img, (x1, y1), (x2-1, y2-1), color, 2)
        
        # 検出情報テキスト
        info_lines = []
        if 'class_id' in detection and class_names:
            class_id = int(detection['class_id'])
            class_name = class_names[class_id] if class_id < len(class_names) else f"class_{class_id}"
            info_lines.append(f"Class: {class_name}")
        
        if 'confidence' in detection:
            info_lines.append(f"Conf: {detection['confidence']:.2f}")
        
        if 'track_id' in detection:
            info_lines.append(f"ID: {detection['track_id']}")
        
        # テキスト描画
        font_scale = 0.5
        thickness = 1
        line_height = 20
        
        for j, line in enumerate(info_lines):
            text_x = x1 + 5
            text_y = y1 + 20 + j * line_height
            cv2.putText(summary_img, line, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    
    return summary_img