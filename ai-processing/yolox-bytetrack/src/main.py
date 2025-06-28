#!/usr/bin/env python3
"""
YOLOX + ByteTrack 統合メインスクリプト
全コンポーネントを統合して物体検出・追跡を実行
"""

import argparse
import sys
import signal
import time
from pathlib import Path
from typing import Optional

# 自作モジュールインポート
from config_loader import load_config, ConfigValidationError
from yolox_wrapper import YOLOXWrapper
from bytetrack_wrapper import ByteTrackWrapper
from video_processor import VideoProcessor
from utils.log_utils import setup_logger, log_system_info, log_config_summary, PerformanceLogger
from utils.time_utils import Timer


class YOLOXByteTrackApp:
    """YOLOX + ByteTrack アプリケーションクラス"""
    
    def __init__(self, config_path: str):
        """
        初期化
        
        Args:
            config_path: 設定ファイルパス
        """
        self.config_path = config_path
        self.config = None
        self.logger = None
        
        # コンポーネント
        self.yolox = None
        self.bytetrack = None
        self.video_processor = None
        
        # 実行制御
        self.running = True
        self.performance_logger = None
        
        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラー（Ctrl+C対応）"""
        self.logger.info("終了シグナル受信。処理を停止中...")
        self.running = False
    
    def initialize(self):
        """アプリケーション初期化"""
        print("YOLOX + ByteTrack 物体検出・追跡システム")
        print("=" * 50)
        
        # 設定読み込み
        try:
            self.config = load_config(self.config_path)
            print(f"✓ 設定ファイル読み込み完了: {self.config_path}")
        except (FileNotFoundError, ConfigValidationError) as e:
            print(f"✗ 設定ファイルエラー: {e}")
            return False
        except Exception as e:
            print(f"✗ 予期しないエラー: {e}")
            return False
        
        # ログ設定
        try:
            self.logger = setup_logger(
                name="yolox_bytetrack",
                log_file=self.config.output.log_path if self.config.output.save_logs else None,
                log_level=self.config.output.log_level,
                console_output=True,
                file_output=self.config.output.save_logs
            )
            print("✓ ログ設定完了")
        except Exception as e:
            print(f"✗ ログ設定エラー: {e}")
            return False
        
        # システム情報ログ
        log_system_info(self.logger)
        log_config_summary(self.logger, self.config)
        
        # コンポーネント初期化
        if not self._initialize_components():
            return False
        
        print("✓ 初期化完了")
        print("=" * 50)
        return True
    
    def _initialize_components(self):
        """コンポーネント初期化"""
        try:
            # YOLOX初期化
            self.logger.info("YOLOX初期化開始")
            self.yolox = YOLOXWrapper(self.config.yolox, self.logger)
            self.logger.info("YOLOX初期化完了")
            
            # ByteTrack初期化
            self.logger.info("ByteTrack初期化開始")
            self.bytetrack = ByteTrackWrapper(self.config.bytetrack, self.logger)
            self.logger.info("ByteTrack初期化完了")
            
            # 動画処理器初期化
            self.logger.info("動画処理器初期化開始")
            self.video_processor = VideoProcessor(self.config, self.logger)
            self.logger.info("動画処理器初期化完了")
            
            # パフォーマンスロガー
            self.performance_logger = PerformanceLogger(
                self.logger, 
                self.config.performance.stats_interval
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"コンポーネント初期化失敗: {e}")
            return False
    
    def run(self):
        """メイン処理実行"""
        if not self.running:
            return False
        
        self.logger.info("処理開始")
        total_timer = Timer("総処理時間")
        
        try:
            with self.video_processor as processor:
                processor.initialize()
                
                # フレーム処理ループ
                for frame, metadata in processor.process_frames():
                    if not self.running:
                        self.logger.info("ユーザー中断")
                        break
                    
                    # フレーム処理
                    detection_result = self._process_frame(frame, metadata)
                    
                    if detection_result is None:
                        continue
                    
                    # 結果描画
                    rendered_frame = processor.render_frame(
                        frame, 
                        detection_result['tracks'], 
                        detection_result['stats']
                    )
                    
                    # 結果保存
                    processor.save_result(
                        rendered_frame, 
                        detection_result['tracks'], 
                        metadata
                    )
                    
                    # リアルタイム表示
                    if not processor.display_frame(rendered_frame):
                        self.logger.info("表示ウィンドウ終了")
                        break
                    
                    # パフォーマンスログ
                    self.performance_logger.log_frame_stats(
                        detection_result['stats']['inference_time'],
                        detection_result['stats']['tracking_time'],
                        detection_result['stats']['total_time']
                    )
                
                # 最終処理
                total_time = total_timer.stop()
                final_stats = self.bytetrack.get_statistics()
                final_stats['total_processing_time'] = total_time
                
                processor.finalize(final_stats)
                self.performance_logger.log_final_summary()
            
            self.logger.info(f"処理完了 - 総処理時間: {total_time:.2f}秒")
            return True
            
        except Exception as e:
            self.logger.error(f"処理中エラー: {e}")
            return False
    
    def _process_frame(self, frame, metadata):
        """
        フレーム処理
        
        Args:
            frame: 入力フレーム
            metadata: フレームメタデータ
            
        Returns:
            Dict: 処理結果
        """
        frame_timer = Timer("フレーム処理")
        frame_timer.start()
        
        try:
            # YOLOX物体検出
            detection_timer = Timer("物体検出")
            detection_timer.start()
            detections = self.yolox.detect(frame)
            detection_time = detection_timer.stop()
            
            # ByteTrack追跡
            tracking_timer = Timer("追跡処理")
            tracking_timer.start()
            tracks = self.bytetrack.update(detections)
            tracking_time = tracking_timer.stop()
            
            total_time = frame_timer.stop()
            
            # デバッグ情報
            if self.config.debug.verbose:
                self.logger.debug(
                    f"Frame {metadata['frame_id']}: "
                    f"{len(detections['boxes'])} detections, "
                    f"{len(tracks)} tracks, "
                    f"detection: {detection_time*1000:.1f}ms, "
                    f"tracking: {tracking_time*1000:.1f}ms"
                )
            
            # 統計情報作成
            stats = {
                'frame_id': metadata['frame_id'],
                'processing_fps': metadata.get('processing_fps', 0),
                'detections_count': len(detections['boxes']),
                'tracks_count': len(tracks),
                'inference_time': detections['inference_time'],
                'tracking_time': tracking_time,
                'total_time': total_time,
                'preprocessing_time': detections.get('preprocessing_time', 0),
                'postprocessing_time': detections.get('postprocessing_time', 0)
            }
            
            return {
                'detections': detections,
                'tracks': tracks,
                'stats': stats
            }
            
        except Exception as e:
            self.logger.error(f"フレーム処理エラー (Frame {metadata['frame_id']}): {e}")
            return None
    
    def cleanup(self):
        """リソースクリーンアップ"""
        self.logger.info("クリーンアップ開始")
        
        if self.yolox:
            self.yolox.cleanup()
        
        if self.bytetrack:
            self.bytetrack.cleanup()
        
        if self.video_processor:
            self.video_processor.cleanup()
        
        self.logger.info("クリーンアップ完了")
    
    def get_summary(self):
        """実行サマリー取得"""
        summary = {
            'yolox_info': self.yolox.get_model_info() if self.yolox else {},
            'bytetrack_info': self.bytetrack.get_tracker_info() if self.bytetrack else {},
            'performance': self.performance_logger.get_final_summary() if self.performance_logger else {}
        }
        return summary


def create_parser():
    """コマンドライン引数パーサー作成"""
    parser = argparse.ArgumentParser(
        description="YOLOX + ByteTrack 物体検出・追跡システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py --config config.yml
  python main.py --config configs/webcam.yml
  python main.py --config configs/video.yml --debug
  python main.py --config configs/rtsp.yml --benchmark
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="設定ファイルパス (YAML)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="デバッグモード有効化"
    )
    
    parser.add_argument(
        "--benchmark",
        action="store_true", 
        help="ベンチマークモード（推論速度測定）"
    )
    
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="リアルタイム表示無効化"
    )
    
    parser.add_argument(
        "--output-dir",
        help="出力ディレクトリ上書き"
    )
    
    return parser


def run_benchmark(app: YOLOXByteTrackApp):
    """ベンチマーク実行"""
    print("=" * 50)
    print("ベンチマーク実行")
    print("=" * 50)
    
    if not app.yolox:
        print("✗ YOLOXが初期化されていません")
        return
    
    # YOLOX推論ベンチマーク
    print("YOLOX推論速度ベンチマーク実行中...")
    benchmark_result = app.yolox.benchmark(num_runs=100)
    
    print(f"平均推論時間: {benchmark_result['mean_time']*1000:.1f}ms")
    print(f"平均FPS: {benchmark_result['mean_fps']:.1f}")
    print(f"最小時間: {benchmark_result['min_time']*1000:.1f}ms")
    print(f"最大時間: {benchmark_result['max_time']*1000:.1f}ms")
    print(f"標準偏差: {benchmark_result['std_time']*1000:.1f}ms")
    print("=" * 50)


def main():
    """メイン関数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 設定ファイル存在確認
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"✗ 設定ファイルが見つかりません: {config_path}")
        return 1
    
    app = None
    try:
        # アプリケーション作成・初期化
        app = YOLOXByteTrackApp(str(config_path))
        
        if not app.initialize():
            print("✗ 初期化失敗")
            return 1
        
        # 設定上書き
        if args.debug:
            app.config.debug.enabled = True
            app.config.debug.verbose = True
        
        if args.no_display:
            app.config.display.show_realtime = False
        
        if args.output_dir:
            app.config.output.output_dir = args.output_dir
        
        # ベンチマークモード
        if args.benchmark:
            run_benchmark(app)
            return 0
        
        # メイン処理実行
        success = app.run()
        
        if success:
            print("✓ 処理正常終了")
            
            # サマリー表示
            summary = app.get_summary()
            if summary.get('performance'):
                perf = summary['performance']
                print(f"最終統計 - 総フレーム数: {perf.get('total_frames', 0)}, "
                      f"平均FPS: {perf.get('average_fps', 0):.2f}")
            
            return 0
        else:
            print("✗ 処理異常終了")
            return 1
            
    except KeyboardInterrupt:
        print("\n✓ ユーザー中断")
        return 0
    except Exception as e:
        print(f"✗ 予期しないエラー: {e}")
        return 1
    finally:
        if app:
            app.cleanup()


if __name__ == "__main__":
    sys.exit(main())