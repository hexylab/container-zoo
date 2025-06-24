#!/usr/bin/env python3
"""
CUDA + TensorRT + ONNX環境テスト用スクリプト
Docker環境が正しく構築されているかをテストします
"""

import sys
import platform

def test_basic_imports():
    """基本的なライブラリのインポートテスト"""
    print("=== 基本ライブラリのインポートテスト ===")
    
    try:
        import numpy as np
        print(f"✓ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
    
    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV: {e}")
    
    try:
        from PIL import Image
        print(f"✓ Pillow: インポート成功")
    except ImportError as e:
        print(f"✗ Pillow: {e}")

def test_cuda():
    """CUDA環境のテスト"""
    print("\n=== CUDA環境テスト ===")
    
    try:
        import torch
        print(f"✓ PyTorch: {torch.__version__}")
        print(f"✓ CUDA利用可能: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"✓ CUDA デバイス数: {torch.cuda.device_count()}")
            print(f"✓ CUDA デバイス名: {torch.cuda.get_device_name(0)}")
            print(f"✓ CUDA バージョン: {torch.version.cuda}")
    except ImportError as e:
        print(f"✗ PyTorch: {e}")

def test_onnx():
    """ONNX環境のテスト"""
    print("\n=== ONNX環境テスト ===")
    
    try:
        import onnx
        print(f"✓ ONNX: {onnx.__version__}")
    except ImportError as e:
        print(f"✗ ONNX: {e}")
    
    try:
        import onnxruntime as ort
        print(f"✓ ONNX Runtime: {ort.__version__}")
        providers = ort.get_available_providers()
        print(f"✓ 利用可能なプロバイダー: {providers}")
        if 'CUDAExecutionProvider' in providers:
            print("✓ CUDA実行プロバイダー利用可能")
        else:
            print("⚠ CUDA実行プロバイダー利用不可")
    except ImportError as e:
        print(f"✗ ONNX Runtime: {e}")

def test_tensorrt():
    """TensorRT環境のテスト"""
    print("\n=== TensorRT環境テスト ===")
    
    try:
        import tensorrt as trt
        print(f"✓ TensorRT: {trt.__version__}")
    except ImportError as e:
        print(f"✗ TensorRT: {e}")

def test_video_processing():
    """動画処理ライブラリのテスト"""
    print("\n=== 動画処理ライブラリテスト ===")
    
    try:
        import moviepy
        print(f"✓ MoviePy: インポート成功")
    except ImportError as e:
        print(f"✗ MoviePy: {e}")
    
    try:
        import av
        print(f"✓ PyAV: {av.__version__}")
    except ImportError as e:
        print(f"✗ PyAV: {e}")

def create_simple_test():
    """簡単な処理テストを実行"""
    print("\n=== 簡単な処理テスト ===")
    
    try:
        import numpy as np
        import cv2
        
        # ダミー画像作成
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:50, :50] = [255, 0, 0]  # 青い正方形
        img[50:, 50:] = [0, 255, 0]  # 緑の正方形
        
        # OpenCVで画像処理
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        print("✓ OpenCVによる画像処理テスト成功")
        
        # PyTorchテスト（CUDA利用可能な場合）
        try:
            import torch
            if torch.cuda.is_available():
                tensor = torch.tensor(img, dtype=torch.float32).cuda()
                result = tensor.mean()
                print(f"✓ CUDA Tensorテスト成功: 平均値 = {result.item():.2f}")
            else:
                tensor = torch.tensor(img, dtype=torch.float32)
                result = tensor.mean()
                print(f"✓ CPU Tensorテスト成功: 平均値 = {result.item():.2f}")
        except ImportError:
            print("⚠ PyTorchが利用できないためTensorテストはスキップ")
            
    except Exception as e:
        print(f"✗ 処理テストエラー: {e}")

def main():
    """メイン実行関数"""
    print("CUDA + TensorRT + ONNX 環境テスト開始")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print("=" * 50)
    
    test_basic_imports()
    test_cuda()
    test_onnx()
    test_tensorrt()
    test_video_processing()
    create_simple_test()
    
    print("\n" + "=" * 50)
    print("環境テスト完了")

if __name__ == "__main__":
    main()