#!/usr/bin/env python3
"""
時刻・時間管理ユーティリティ
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Union


def get_timestamp(format_str: str = "%Y%m%d_%H%M%S") -> str:
    """
    現在時刻のタイムスタンプを取得
    
    Args:
        format_str: 時刻フォーマット
        
    Returns:
        str: フォーマット済みタイムスタンプ
    """
    return datetime.now().strftime(format_str)


def get_iso_timestamp() -> str:
    """
    ISO形式のタイムスタンプを取得
    
    Returns:
        str: ISO形式タイムスタンプ
    """
    return datetime.now().isoformat()


def format_duration(seconds: float) -> str:
    """
    秒数を読みやすい形式に変換
    
    Args:
        seconds: 秒数
        
    Returns:
        str: フォーマット済み時間
    """
    if seconds < 60:
        return f"{seconds:.2f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}分"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}時間"


def format_elapsed_time(start_time: float) -> str:
    """
    開始時刻からの経過時間を取得
    
    Args:
        start_time: 開始時刻（time.time()の値）
        
    Returns:
        str: 経過時間
    """
    elapsed = time.time() - start_time
    return format_duration(elapsed)


class Timer:
    """シンプルなタイマークラス"""
    
    def __init__(self, name: str = "Timer"):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.laps: list = []
    
    def start(self) -> 'Timer':
        """タイマー開始"""
        self.start_time = time.time()
        self.end_time = None
        self.laps.clear()
        return self
    
    def stop(self) -> float:
        """
        タイマー停止
        
        Returns:
            float: 経過時間（秒）
        """
        if self.start_time is None:
            raise RuntimeError("タイマーが開始されていません")
        
        self.end_time = time.time()
        return self.elapsed()
    
    def lap(self, label: str = "") -> float:
        """
        ラップタイム記録
        
        Args:
            label: ラップのラベル
            
        Returns:
            float: 開始からの経過時間
        """
        if self.start_time is None:
            raise RuntimeError("タイマーが開始されていません")
        
        lap_time = time.time()
        elapsed = lap_time - self.start_time
        
        self.laps.append({
            'label': label or f"Lap {len(self.laps) + 1}",
            'time': lap_time,
            'elapsed': elapsed
        })
        
        return elapsed
    
    def elapsed(self) -> float:
        """
        経過時間を取得
        
        Returns:
            float: 経過時間（秒）
        """
        if self.start_time is None:
            return 0.0
        
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def get_summary(self) -> str:
        """
        タイマーサマリーを取得
        
        Returns:
            str: サマリー文字列
        """
        if self.start_time is None:
            return f"{self.name}: 未開始"
        
        total_elapsed = self.elapsed()
        summary = [f"{self.name}: {format_duration(total_elapsed)}"]
        
        if self.laps:
            summary.append("ラップタイム:")
            prev_time = 0
            for lap in self.laps:
                lap_duration = lap['elapsed'] - prev_time
                summary.append(f"  {lap['label']}: {format_duration(lap_duration)} (累計: {format_duration(lap['elapsed'])})")
                prev_time = lap['elapsed']
        
        return "\n".join(summary)
    
    def __enter__(self) -> 'Timer':
        """コンテキストマネージャー開始"""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        self.stop()


class FPSCounter:
    """FPS計測クラス"""
    
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times = []
        self.last_time = time.time()
    
    def update(self) -> float:
        """
        フレーム更新とFPS計算
        
        Returns:
            float: 現在のFPS
        """
        current_time = time.time()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(frame_time)
        
        # ウィンドウサイズを超えた場合は古いデータを削除
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        
        return self.get_fps()
    
    def get_fps(self) -> float:
        """
        現在のFPSを取得
        
        Returns:
            float: FPS値
        """
        if not self.frame_times:
            return 0.0
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def reset(self):
        """FPSカウンターをリセット"""
        self.frame_times.clear()
        self.last_time = time.time()


class ProgressTracker:
    """進捗追跡クラス"""
    
    def __init__(self, total: int, name: str = "Progress"):
        self.total = total
        self.name = name
        self.current = 0
        self.start_time = time.time()
    
    def update(self, increment: int = 1) -> dict:
        """
        進捗更新
        
        Args:
            increment: 進捗増分
            
        Returns:
            dict: 進捗情報
        """
        self.current += increment
        elapsed = time.time() - self.start_time
        
        progress_ratio = self.current / self.total if self.total > 0 else 0
        
        # 推定残り時間
        if progress_ratio > 0:
            estimated_total_time = elapsed / progress_ratio
            eta = estimated_total_time - elapsed
        else:
            eta = 0
        
        return {
            'current': self.current,
            'total': self.total,
            'progress_ratio': progress_ratio,
            'progress_percent': progress_ratio * 100,
            'elapsed': elapsed,
            'eta': eta,
            'rate': self.current / elapsed if elapsed > 0 else 0
        }
    
    def get_status_string(self) -> str:
        """
        進捗状況文字列を取得
        
        Returns:
            str: 進捗状況
        """
        info = self.update(0)  # 更新せずに情報取得
        
        percent = info['progress_percent']
        elapsed_str = format_duration(info['elapsed'])
        eta_str = format_duration(info['eta'])
        rate = info['rate']
        
        return (f"{self.name}: {self.current}/{self.total} "
                f"({percent:.1f}%) | "
                f"経過: {elapsed_str} | "
                f"残り: {eta_str} | "
                f"速度: {rate:.2f}/秒")


def sleep_fps(target_fps: float, last_time: float) -> float:
    """
    指定FPSになるよう適切にsleep
    
    Args:
        target_fps: 目標FPS
        last_time: 前回の処理時刻
        
    Returns:
        float: 現在時刻
    """
    if target_fps <= 0:
        return time.time()
    
    target_frame_time = 1.0 / target_fps
    elapsed = time.time() - last_time
    sleep_time = target_frame_time - elapsed
    
    if sleep_time > 0:
        time.sleep(sleep_time)
    
    return time.time()