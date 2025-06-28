#!/usr/bin/env python3
"""
YOLOX + ByteTrack 環境テスト用スクリプト
Docker環境が正しく構築されているかをテストします
"""

import sys
import platform
import subprocess
import time
import numpy as np
from pathlib import Path


def print_header(title: str):
    """ヘッダー出力"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """セクション出力"""
    print(f"\n--- {title} ---")


def test_basic_environment():
    """基本環境テスト"""
    print_section("基本環境情報")
    
    try:
        print(f"✓ Python: {sys.version}")
        print(f"✓ Platform: {platform.platform()}")
        print(f"✓ Architecture: {platform.architecture()}")
        print(f"✓ Processor: {platform.processor()}")
        return True
    except Exception as e:
        print(f"✗ 基本環境エラー: {e}")
        return False


def test_basic_imports():
    """基本ライブラリのインポートテスト"""
    print_section("基本ライブラリテスト")
    
    import_tests = [
        ("numpy", "np"),
        ("cv2", "cv2"),
        ("yaml", "yaml"),
        ("PIL", "Image"),
        ("pathlib", "Path"),
        ("logging", "logging"),
        ("json", "json"),
        ("time", "time"),
        ("datetime", "datetime"),
        ("collections", "defaultdict"),
        ("typing", "Dict, List, Optional"),
    ]
    
    success_count = 0
    for module_name, import_name in import_tests:
        try:
            exec(f"import {import_name}")
            print(f"✓ {module_name}: インポート成功")
            success_count += 1
        except ImportError as e:
            print(f"✗ {module_name}: {e}")
    
    print(f"\n基本ライブラリ: {success_count}/{len(import_tests)} 成功")
    return success_count == len(import_tests)


def test_deep_learning_libraries():
    """深層学習ライブラリテスト"""
    print_section("深層学習ライブラリテスト")
    
    # PyTorch
    try:
        import torch
        import torchvision
        print(f"✓ PyTorch: {torch.__version__}")
        print(f"✓ TorchVision: {torchvision.__version__}")
        pytorch_ok = True
    except ImportError as e:
        print(f"✗ PyTorch: {e}")
        pytorch_ok = False
    
    # 追加ライブラリ
    additional_libs = [
        ("scikit-learn", "sklearn"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("pandas", "pandas"),
        ("scipy", "scipy"),
        ("tqdm", "tqdm"),
    ]
    
    success_count = 0
    for lib_name, import_name in additional_libs:
        try:
            exec(f"import {import_name}")
            print(f"✓ {lib_name}: インポート成功")
            success_count += 1
        except ImportError as e:
            print(f"✗ {lib_name}: {e}")
    
    return pytorch_ok and success_count >= len(additional_libs) * 0.8


def test_cuda_environment():
    """CUDA環境テスト"""
    print_section("CUDA環境テスト")
    
    try:
        import torch
        
        cuda_available = torch.cuda.is_available()
        print(f"✓ CUDA利用可能: {cuda_available}")
        
        if cuda_available:
            device_count = torch.cuda.device_count()
            print(f"✓ CUDA デバイス数: {device_count}")
            
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                print(f"✓ GPU {i}: {device_name}")
                
                # GPU メモリ情報
                props = torch.cuda.get_device_properties(i)
                total_memory = props.total_memory / (1024**3)
                print(f"  メモリ: {total_memory:.1f} GB")
            
            print(f"✓ CUDA バージョン: {torch.version.cuda}")
            
            # 簡単なCUDAテスト
            try:
                x = torch.tensor([1.0, 2.0]).cuda()
                y = x * 2
                result = y.cpu().numpy()
                print(f"✓ CUDA演算テスト成功: {result}")
                return True
            except Exception as e:
                print(f"✗ CUDA演算テスト失敗: {e}")
                return False
        else:
            print("⚠ CUDA未対応環境（CPUモード）")
            return True
            
    except ImportError:
        print("✗ PyTorchがインストールされていません")
        return False


def test_yolox_environment():
    """YOLOX環境テスト"""
    print_section("YOLOX環境テスト")
    
    try:
        # YOLOX パスチェック
        yolox_path = Path("/workspace/YOLOX")
        if yolox_path.exists():
            print(f"✓ YOLOXリポジトリ: {yolox_path}")
        else:
            print(f"✗ YOLOXリポジトリが見つかりません: {yolox_path}")
            return False
        
        # YOLOX インポートテスト
        sys.path.append(str(yolox_path))
        
        from yolox.exp import get_exp
        print("✓ YOLOX exp モジュール: インポート成功")
        
        from yolox.utils import postprocess
        print("✓ YOLOX utils モジュール: インポート成功")
        
        from yolox.data.data_augment import ValTransform
        print("✓ YOLOX data モジュール: インポート成功")
        
        # モデル作成テスト
        try:
            exp = get_exp(None, "yolox_s")
            model = exp.get_model()
            print("✓ YOLOXモデル作成: 成功")
            
            # パラメータ数確認
            num_params = sum(p.numel() for p in model.parameters())
            print(f"✓ モデルパラメータ数: {num_params:,}")
            
            return True
        except Exception as e:
            print(f"✗ YOLOXモデル作成失敗: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ YOLOX インポートエラー: {e}")
        return False


def test_bytetrack_environment():
    """ByteTrack環境テスト"""
    print_section("ByteTrack環境テスト")
    
    try:
        # ByteTrack パスチェック
        bytetrack_path = Path("/workspace/ByteTrack")
        if bytetrack_path.exists():
            print(f"✓ ByteTrackリポジトリ: {bytetrack_path}")
        else:
            print(f"✗ ByteTrackリポジトリが見つかりません: {bytetrack_path}")
            return False
        
        # ByteTrack インポートテスト
        sys.path.append(str(bytetrack_path))
        
        from yolox.tracker.byte_tracker import BYTETracker
        print("✓ ByteTracker: インポート成功")
        
        from yolox.tracking_utils.timer import Timer
        print("✓ ByteTrack Timer: インポート成功")
        
        # ByteTracker作成テスト
        try:
            class Args:
                def __init__(self):
                    self.track_thresh = 0.5
                    self.track_buffer = 30
                    self.match_thresh = 0.8
                    self.aspect_ratio_thresh = 1.6
                    self.min_box_area = 10
                    self.mot20 = False
            
            args = Args()
            tracker = BYTETracker(args, frame_rate=30)
            print("✓ ByteTracker作成: 成功")
            
            return True
        except Exception as e:
            print(f"✗ ByteTracker作成失敗: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ ByteTrack インポートエラー: {e}")
        return False


def test_opencv_functionality():
    """OpenCV機能テスト"""
    print_section("OpenCV機能テスト")
    
    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
        
        # ダミー画像作成
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:50, :50] = [255, 0, 0]  # 青い正方形
        img[50:, 50:] = [0, 255, 0]  # 緑の正方形
        
        # 基本的な画像処理
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print("✓ 色変換: 成功")
        
        edges = cv2.Canny(gray, 50, 150)
        print("✓ エッジ検出: 成功")
        
        resized = cv2.resize(img, (200, 200))
        print("✓ リサイズ: 成功")
        
        # ビデオコーデック確認
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        print("✓ 動画コーデック: 利用可能")
        
        return True
        
    except Exception as e:
        print(f"✗ OpenCV機能テスト失敗: {e}")
        return False


def test_custom_modules():
    """カスタムモジュールテスト"""
    print_section("カスタムモジュールテスト")
    
    try:
        # src ディレクトリをパスに追加
        src_path = Path("/workspace/src")
        if src_path.exists():
            sys.path.insert(0, str(src_path))
            print(f"✓ srcパス追加: {src_path}")
        else:
            print(f"✗ srcディレクトリが見つかりません: {src_path}")
            return False
        
        # カスタムモジュールインポートテスト
        modules_to_test = [
            "config_loader",
            "yolox_wrapper", 
            "bytetrack_wrapper",
            "video_processor",
            "utils.file_utils",
            "utils.time_utils", 
            "utils.log_utils",
            "utils.video_utils",
            "utils.visualization"
        ]
        
        success_count = 0
        for module in modules_to_test:
            try:
                exec(f"import {module}")
                print(f"✓ {module}: インポート成功")
                success_count += 1
            except ImportError as e:
                print(f"✗ {module}: {e}")
        
        print(f"\nカスタムモジュール: {success_count}/{len(modules_to_test)} 成功")
        return success_count >= len(modules_to_test) * 0.9
        
    except Exception as e:
        print(f"✗ カスタムモジュールテストエラー: {e}")
        return False


def test_config_loading():
    """設定ファイル読み込みテスト"""
    print_section("設定ファイル読み込みテスト")
    
    try:
        from config_loader import load_config
        
        # メイン設定ファイル
        config_path = Path("/workspace/config.yml")
        if config_path.exists():
            config = load_config(config_path)
            print(f"✓ メイン設定ファイル読み込み: {config_path}")
            print(f"  入力タイプ: {config.input.type}")
            print(f"  YOLOXモデル: {config.yolox.model_size}")
        else:
            print(f"✗ メイン設定ファイルが見つかりません: {config_path}")
            return False
        
        # サブ設定ファイル
        configs_dir = Path("/workspace/configs")
        if configs_dir.exists():
            config_files = list(configs_dir.glob("*.yml"))
            print(f"✓ サブ設定ファイル数: {len(config_files)}")
            
            for config_file in config_files:
                try:
                    sub_config = load_config(config_file)
                    print(f"  ✓ {config_file.name}: 読み込み成功")
                except Exception as e:
                    print(f"  ✗ {config_file.name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ 設定ファイル読み込みエラー: {e}")
        return False


def test_model_availability():
    """モデルファイル確認テスト"""
    print_section("モデルファイル確認")
    
    models_dir = Path("/workspace/models")
    if not models_dir.exists():
        print(f"✗ modelsディレクトリが見つかりません: {models_dir}")
        return False
    
    print(f"✓ modelsディレクトリ: {models_dir}")
    
    # YOLOXモデルファイル確認
    model_files = list(models_dir.glob("*.pth"))
    print(f"✓ 検出されたモデルファイル数: {len(model_files)}")
    
    for model_file in model_files:
        size = model_file.stat().st_size / (1024**2)  # MB
        print(f"  ✓ {model_file.name}: {size:.1f} MB")
    
    # 推奨モデルファイル
    recommended_models = [
        "yolox_s.pth",
        "yolox_m.pth", 
        "yolox_l.pth"
    ]
    
    available_count = 0
    for model_name in recommended_models:
        model_path = models_dir / model_name
        if model_path.exists():
            size = model_path.stat().st_size / (1024**2)
            print(f"  ✓ {model_name}: 利用可能 ({size:.1f} MB)")
            available_count += 1
        else:
            print(f"  ⚠ {model_name}: 未ダウンロード")
    
    if available_count == 0:
        print("⚠ 推奨モデルが見つかりません。初回実行時に自動ダウンロードされます。")
    
    return True


def test_integration():
    """統合テスト"""
    print_section("統合テスト")
    
    try:
        # 設定読み込み
        from config_loader import load_config
        config_path = Path("/workspace/config.yml")
        config = load_config(config_path)
        print("✓ 設定読み込み: 成功")
        
        # YOLOXラッパー初期化テスト
        from yolox_wrapper import YOLOXWrapper
        try:
            yolox = YOLOXWrapper(config.yolox)
            print("✓ YOLOXラッパー初期化: 成功")
            
            # モデル情報取得
            model_info = yolox.get_model_info()
            print(f"  モデルサイズ: {model_info['model_size']}")
            print(f"  入力サイズ: {model_info['input_size']}")
            print(f"  デバイス: {model_info['device']}")
            
            yolox.cleanup()
        except Exception as e:
            print(f"✗ YOLOXラッパー初期化失敗: {e}")
            return False
        
        # ByteTrackラッパー初期化テスト
        from bytetrack_wrapper import ByteTrackWrapper
        try:
            bytetrack = ByteTrackWrapper(config.bytetrack)
            print("✓ ByteTrackラッパー初期化: 成功")
            
            tracker_info = bytetrack.get_tracker_info()
            print(f"  追跡閾値: {tracker_info['config']['track_thresh']}")
            print(f"  フレームレート: {tracker_info['config']['frame_rate']}")
            
            bytetrack.cleanup()
        except Exception as e:
            print(f"✗ ByteTrackラッパー初期化失敗: {e}")
            return False
        
        print("✓ 統合テスト: 全て成功")
        return True
        
    except Exception as e:
        print(f"✗ 統合テストエラー: {e}")
        return False


def test_performance():
    """パフォーマンステスト"""
    print_section("パフォーマンステスト")
    
    try:
        import torch
        
        # CPU/GPU性能テスト
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"✓ テストデバイス: {device}")
        
        # 簡単な演算ベンチマーク
        size = 1000
        x = torch.randn(size, size, device=device)
        y = torch.randn(size, size, device=device)
        
        start_time = time.time()
        for _ in range(10):
            z = torch.matmul(x, y)
        torch.cuda.synchronize() if device.type == "cuda" else None
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"✓ 行列演算 ({size}x{size}): {avg_time*1000:.1f}ms")
        
        if device.type == "cuda":
            # GPU メモリ使用量
            memory_allocated = torch.cuda.memory_allocated() / (1024**2)
            memory_cached = torch.cuda.memory_reserved() / (1024**2)
            print(f"✓ GPU メモリ使用量: {memory_allocated:.1f} MB")
            print(f"✓ GPU メモリキャッシュ: {memory_cached:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"✗ パフォーマンステストエラー: {e}")
        return False


def run_all_tests():
    """全テスト実行"""
    print_header("YOLOX + ByteTrack 環境テスト")
    
    tests = [
        ("基本環境", test_basic_environment),
        ("基本ライブラリ", test_basic_imports),
        ("深層学習ライブラリ", test_deep_learning_libraries),
        ("CUDA環境", test_cuda_environment),
        ("OpenCV機能", test_opencv_functionality),
        ("YOLOX環境", test_yolox_environment),
        ("ByteTrack環境", test_bytetrack_environment),
        ("カスタムモジュール", test_custom_modules),
        ("設定ファイル", test_config_loading),
        ("モデルファイル", test_model_availability),
        ("統合テスト", test_integration),
        ("パフォーマンス", test_performance),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            print_header(f"{test_name}テスト")
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name}テスト中にエラー: {e}")
            results[test_name] = False
    
    # 結果サマリー
    print_header("テスト結果サマリー")
    
    passed_count = 0
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {test_name}")
        if result:
            passed_count += 1
    
    total_tests = len(results)
    pass_rate = (passed_count / total_tests) * 100
    
    print(f"\n総テスト数: {total_tests}")
    print(f"成功: {passed_count}")
    print(f"失敗: {total_tests - passed_count}")
    print(f"成功率: {pass_rate:.1f}%")
    
    if pass_rate >= 90:
        print("\n🎉 環境は正常に構築されています！")
    elif pass_rate >= 70:
        print("\n⚠ 環境はほぼ正常ですが、いくつかの問題があります。")
    else:
        print("\n❌ 環境に重大な問題があります。設定を確認してください。")
    
    return pass_rate >= 70


def main():
    """メイン関数"""
    try:
        success = run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠ テスト中断")
        return 1
    except Exception as e:
        print(f"\n\n✗ 予期しないエラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())