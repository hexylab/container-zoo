#!/usr/bin/env python3
"""
SigLIP2環境テスト用スクリプト
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
        import PIL
        print(f"✓ Pillow: {PIL.__version__}")
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


def test_transformers():
    """Transformers環境のテスト"""
    print("\n=== Transformers環境テスト ===")

    try:
        import transformers
        print(f"✓ Transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"✗ Transformers: {e}")

    try:
        import huggingface_hub
        print(f"✓ Hugging Face Hub: {huggingface_hub.__version__}")
    except ImportError as e:
        print(f"✗ Hugging Face Hub: {e}")


def test_siglip2_model():
    """SigLIP2モデルのテスト"""
    print("\n=== SigLIP2モデルテスト ===")

    try:
        from transformers import AutoModel, AutoProcessor
        import torch

        model_name = "google/siglip2-base-patch16-256"

        # モデルがキャッシュされているか確認
        print(f"モデル: {model_name}")

        # プロセッサの読み込みテスト
        processor = AutoProcessor.from_pretrained(model_name)
        print("✓ プロセッサの読み込み成功")

        # モデルの読み込みテスト
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = AutoModel.from_pretrained(model_name).to(device)
        print(f"✓ モデルの読み込み成功 (デバイス: {device})")

        # 簡単な推論テスト
        from PIL import Image
        import numpy as np

        dummy_image = Image.fromarray(np.zeros((256, 256, 3), dtype=np.uint8))
        inputs = processor(images=dummy_image, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.get_image_features(**inputs)

        print(f"✓ 推論テスト成功 (出力shape: {outputs.shape})")

    except Exception as e:
        print(f"✗ SigLIP2テストエラー: {e}")


def main():
    """メイン実行関数"""
    print("SigLIP2 環境テスト開始")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print("=" * 50)

    test_basic_imports()
    test_cuda()
    test_transformers()
    test_siglip2_model()

    print("\n" + "=" * 50)
    print("環境テスト完了")


if __name__ == "__main__":
    main()
