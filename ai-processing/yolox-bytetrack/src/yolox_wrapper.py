#!/usr/bin/env python3
"""
YOLOXラッパークラス
YOLOX物体検出の統一インターフェースを提供
"""

import os
import sys
import torch
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Union
import logging
import time

# YOLOX関連インポート
sys.path.append('/workspace/YOLOX')
from yolox.exp import get_exp
from yolox.utils import postprocess
from yolox.data.data_augment import ValTransform

from config_loader import YOLOXConfig
from utils.video_utils import preprocess_frame, postprocess_boxes
from utils.decorators import handle_initialization, log_performance
from utils.exceptions import ModelLoadError, InferenceError


class YOLOXWrapper:
    """YOLOX検出器ラッパークラス"""
    
    def __init__(self, config: YOLOXConfig, logger: Optional[logging.Logger] = None):
        """
        初期化
        
        Args:
            config: YOLOX設定
            logger: ロガー
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        self.model = None
        self.device = None
        self.exp = None
        self.transform = None
        
        # クラス名（COCO）
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
            'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
        self._initialize()
    
    @handle_initialization("YOLOX")
    def _initialize(self):
        """初期化処理"""
        # デバイス設定
        self._setup_device()
        
        # モデル設定取得
        self._load_experiment()
        
        # モデルロード
        self._load_model()
        
        # 前処理設定
        self._setup_transform()
    
    def _setup_device(self):
        """デバイス設定"""
        if self.config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(self.config.device)
        
        self.logger.info(f"使用デバイス: {self.device}")
        
        # CUDA利用可能性確認
        if self.device.type == "cuda":
            if not torch.cuda.is_available():
                self.logger.warning("CUDAが利用できません。CPUモードに切り替えます。")
                self.device = torch.device("cpu")
            else:
                self.logger.info(f"GPU: {torch.cuda.get_device_name()}")
                self.logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    def _load_experiment(self):
        """実験設定ロード"""
        # モデルサイズに応じた設定ファイル選択
        exp_map = {
            'yolox_nano': 'yolox_nano',
            'yolox_tiny': 'yolox_tiny', 
            'yolox_s': 'yolox_s',
            'yolox_m': 'yolox_m',
            'yolox_l': 'yolox_l',
            'yolox_x': 'yolox_x'
        }
        
        exp_name = exp_map.get(self.config.model_size, 'yolox_s')
        
        try:
            self.exp = get_exp(None, exp_name)
            self.exp.test_conf = self.config.confidence_threshold
            self.exp.nmsthre = self.config.nms_threshold
            self.exp.test_size = tuple(self.config.input_size)
            
            self.logger.info(f"実験設定ロード: {exp_name}")
            self.logger.info(f"入力サイズ: {self.exp.test_size}")
            
        except Exception as e:
            self.logger.error(f"実験設定ロード失敗: {e}")
            raise RuntimeError(f"YOLOX実験設定ロード失敗: {e}")
    
    def _load_model(self):
        """モデルロード"""
        model_path = Path(self.config.model_path)
        
        # モデルファイル存在確認
        if not model_path.exists():
            self.logger.warning(f"モデルファイルが見つかりません: {model_path}")
            self._try_download_model()
        
        try:
            # モデル作成
            self.model = self.exp.get_model()
            self.model.to(self.device)
            
            # 重み読み込み
            if model_path.exists():
                self.logger.info(f"モデル重み読み込み: {model_path}")
                checkpoint = torch.load(str(model_path), map_location=self.device)
                self.model.load_state_dict(checkpoint['model'])
            else:
                self.logger.warning("事前学習済み重みなしで初期化")
            
            # 評価モード
            self.model.eval()
            
            # パラメータ数ログ
            num_params = sum(p.numel() for p in self.model.parameters())
            self.logger.info(f"モデルパラメータ数: {num_params:,}")
            
        except Exception as e:
            self.logger.error(f"モデルロード失敗: {e}")
            raise RuntimeError(f"YOLOXモデルロード失敗: {e}")
    
    def _try_download_model(self):
        """モデルダウンロード試行"""
        model_urls = {
            'yolox_nano': 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.pth',
            'yolox_tiny': 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_tiny.pth',
            'yolox_s': 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth',
            'yolox_m': 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_m.pth',
            'yolox_l': 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_l.pth',
            'yolox_x': 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_x.pth'
        }
        
        url = model_urls.get(self.config.model_size)
        if not url:
            self.logger.warning(f"モデル '{self.config.model_size}' のダウンロードURLが見つかりません")
            return
        
        try:
            import urllib.request
            from tqdm import tqdm
            
            model_path = Path(self.config.model_path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"モデルダウンロード開始: {url}")
            
            def progress_hook(count, block_size, total_size):
                percent = int(count * block_size * 100 / total_size)
                if count % 100 == 0:  # 進捗表示を間引き
                    self.logger.info(f"ダウンロード進捗: {percent}%")
            
            urllib.request.urlretrieve(url, str(model_path), progress_hook)
            self.logger.info(f"モデルダウンロード完了: {model_path}")
            
        except Exception as e:
            self.logger.warning(f"モデルダウンロード失敗: {e}")
    
    def _setup_transform(self):
        """前処理設定"""
        self.transform = ValTransform(legacy=False)
    
    @log_performance("YOLOX推論")
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        物体検出実行
        
        Args:
            frame: 入力フレーム (BGR)
            
        Returns:
            Dict: 検出結果 {
                'boxes': np.ndarray,      # [N, 4] (x1, y1, x2, y2)
                'scores': np.ndarray,     # [N]
                'class_ids': np.ndarray,  # [N]
                'inference_time': float,  # 推論時間
                'preprocessing_time': float,
                'postprocessing_time': float
            }
        """
        start_time = time.time()
        
        # 前処理
        preprocess_start = time.time()
        processed_frame, scale = self._preprocess(frame)
        preprocessing_time = time.time() - preprocess_start
        
        # 推論
        inference_start = time.time()
        with torch.no_grad():
            outputs = self.model(processed_frame)
        inference_time = time.time() - inference_start
        
        # 後処理
        postprocess_start = time.time()
        detections = self._postprocess(outputs, scale, frame.shape[:2])
        postprocessing_time = time.time() - postprocess_start
        
        total_time = time.time() - start_time
        
        self.logger.debug(
            f"検出処理時間 - 前処理: {preprocessing_time*1000:.1f}ms, "
            f"推論: {inference_time*1000:.1f}ms, "
            f"後処理: {postprocessing_time*1000:.1f}ms, "
            f"合計: {total_time*1000:.1f}ms"
        )
        
        return {
            'boxes': detections['boxes'],
            'scores': detections['scores'],
            'class_ids': detections['class_ids'],
            'inference_time': inference_time,
            'preprocessing_time': preprocessing_time,
            'postprocessing_time': postprocessing_time,
            'total_time': total_time
        }
    
    def _preprocess(self, frame: np.ndarray) -> Tuple[torch.Tensor, float]:
        """
        前処理
        
        Args:
            frame: 入力フレーム (BGR)
            
        Returns:
            Tuple[torch.Tensor, float]: 前処理済みテンソル, スケール比
        """
        # フレーム前処理
        processed_frame, scale = preprocess_frame(
            frame, 
            tuple(self.config.input_size),
            normalize=False,  # YOLOXのtransformで正規化
            swap_rb=False     # YOLOXのtransformでRGB変換
        )
        
        # YOLOX用変換
        processed_frame, _ = self.transform(processed_frame, None, self.exp.test_size)
        processed_frame = torch.from_numpy(processed_frame).unsqueeze(0).float().to(self.device)
        
        return processed_frame, scale
    
    def _postprocess(self, outputs: torch.Tensor, scale: float, original_shape: Tuple[int, int]) -> Dict[str, np.ndarray]:
        """
        後処理
        
        Args:
            outputs: モデル出力
            scale: スケール比
            original_shape: 元画像サイズ (height, width)
            
        Returns:
            Dict: 検出結果
        """
        # YOLOX後処理
        outputs = postprocess(
            outputs, 
            self.exp.num_classes, 
            self.config.confidence_threshold,
            self.config.nms_threshold,
            class_agnostic=True
        )
        
        if outputs[0] is None:
            return {
                'boxes': np.array([]).reshape(0, 4),
                'scores': np.array([]),
                'class_ids': np.array([])
            }
        
        output = outputs[0].cpu().numpy()
        
        # 座標変換
        boxes = output[:, 0:4]
        boxes = postprocess_boxes(
            boxes, 
            scale, 
            tuple(self.config.input_size),
            (original_shape[1], original_shape[0])  # (width, height)
        )
        
        scores = output[:, 4] * output[:, 5]  # obj_conf * cls_conf
        class_ids = output[:, 6].astype(int)
        
        # クラスフィルタリング
        if self.config.target_classes:
            mask = np.isin(class_ids, self.config.target_classes)
            boxes = boxes[mask]
            scores = scores[mask]
            class_ids = class_ids[mask]
        
        return {
            'boxes': boxes,
            'scores': scores,
            'class_ids': class_ids
        }
    
    def get_class_name(self, class_id: int) -> str:
        """
        クラスIDからクラス名を取得
        
        Args:
            class_id: クラスID
            
        Returns:
            str: クラス名
        """
        if 0 <= class_id < len(self.class_names):
            return self.class_names[class_id]
        return f"class_{class_id}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        モデル情報取得
        
        Returns:
            Dict: モデル情報
        """
        return {
            'model_size': self.config.model_size,
            'input_size': self.config.input_size,
            'confidence_threshold': self.config.confidence_threshold,
            'nms_threshold': self.config.nms_threshold,
            'target_classes': self.config.target_classes,
            'device': str(self.device),
            'num_classes': len(self.class_names),
            'model_parameters': sum(p.numel() for p in self.model.parameters()) if self.model else 0
        }
    
    def benchmark(self, input_size: Tuple[int, int] = None, num_runs: int = 100) -> Dict[str, float]:
        """
        推論速度ベンチマーク
        
        Args:
            input_size: 入力サイズ (height, width)
            num_runs: 実行回数
            
        Returns:
            Dict: ベンチマーク結果
        """
        if input_size is None:
            input_size = (480, 640)  # デフォルトサイズ
        
        # ダミーフレーム作成
        dummy_frame = np.random.randint(0, 255, (*input_size, 3), dtype=np.uint8)
        
        # ウォームアップ
        for _ in range(10):
            _ = self.detect(dummy_frame)
        
        # ベンチマーク実行
        times = []
        for _ in range(num_runs):
            start_time = time.time()
            _ = self.detect(dummy_frame)
            times.append(time.time() - start_time)
        
        times = np.array(times)
        
        return {
            'mean_time': float(np.mean(times)),
            'std_time': float(np.std(times)),
            'min_time': float(np.min(times)),
            'max_time': float(np.max(times)),
            'mean_fps': float(1.0 / np.mean(times)),
            'num_runs': num_runs,
            'input_size': input_size
        }
    
    def cleanup(self):
        """リソースクリーンアップ"""
        if hasattr(self, 'model') and self.model is not None:
            del self.model
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("YOLOXリソースクリーンアップ完了")
    
    def __del__(self):
        """デストラクタ"""
        self.cleanup()