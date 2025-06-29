#!/usr/bin/env python3
"""
YOLOX + ByteTrack 統合テスト用クイックテスト
実際にYOLOXが動作することを確認
"""

import sys
import numpy as np
import cv2
import torch
from pathlib import Path

# パスを追加
sys.path.append('/workspace/src')
sys.path.append('/workspace/YOLOX')

def test_yolox_basic():
    """YOLOX基本動作テスト"""
    print("=== YOLOX基本動作テスト ===")
    
    try:
        from config_loader import load_config
        from yolox_wrapper import YOLOXWrapper
        
        # 設定読み込み
        config_path = Path("/workspace/config.yml")
        config = load_config(config_path)
        print("✓ 設定読み込み成功")
        
        # YOLOXラッパー初期化
        yolox = YOLOXWrapper(config.yolox)
        print("✓ YOLOX初期化成功")
        
        # ダミー画像作成（640x640 RGB）
        dummy_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        print("✓ ダミー画像作成成功")
        
        # 推論実行
        detections = yolox.detect(dummy_img)
        print(f"✓ 推論成功 - 検出数: {len(detections['boxes'])}")
        print(f"  検出ボックス形状: {detections['boxes'].shape}")
        print(f"  スコア形状: {detections['scores'].shape}")
        print(f"  クラスID形状: {detections['class_ids'].shape}")
        
        # リソースクリーンアップ
        yolox.cleanup()
        print("✓ リソースクリーンアップ成功")
        
        return True
        
    except Exception as e:
        print(f"✗ YOLOX基本動作テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_all():
    """全設定ファイルテスト"""
    print("\n=== 全設定ファイルテスト ===")
    
    try:
        from config_loader import load_config
        
        config_files = [
            "/workspace/config.yml",
            "/workspace/configs/webcam.yml", 
            "/workspace/configs/video.yml",
            "/workspace/configs/rtsp.yml"
        ]
        
        for config_file in config_files:
            config = load_config(Path(config_file))
            print(f"✓ {Path(config_file).name}: 読み込み成功")
            print(f"  入力タイプ: {config.input.type}")
            print(f"  YOLOXモデル: {config.yolox.model_size}")
        
        return True
        
    except Exception as e:
        print(f"✗ 設定ファイルテスト失敗: {e}")
        return False

def test_gpu_memory():
    """GPU メモリ使用量テスト"""
    print("\n=== GPU メモリテスト ===")
    
    try:
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            
            # 初期メモリ
            initial_mem = torch.cuda.memory_allocated(device) / 1024**2
            print(f"✓ 初期GPU メモリ: {initial_mem:.1f} MB")
            
            # 大きなテンソル作成
            x = torch.randn(1000, 1000, device='cuda')
            y = torch.randn(1000, 1000, device='cuda')
            z = torch.matmul(x, y)
            
            # 使用メモリ
            used_mem = torch.cuda.memory_allocated(device) / 1024**2
            print(f"✓ 使用後GPU メモリ: {used_mem:.1f} MB")
            print(f"✓ 増加量: {used_mem - initial_mem:.1f} MB")
            
            # クリーンアップ
            del x, y, z
            torch.cuda.empty_cache()
            
            final_mem = torch.cuda.memory_allocated(device) / 1024**2
            print(f"✓ クリーンアップ後: {final_mem:.1f} MB")
            
            return True
        else:
            print("⚠ CUDA利用不可 - CPUモードでテスト")
            return True
            
    except Exception as e:
        print(f"✗ GPU メモリテスト失敗: {e}")
        return False

def main():
    """メイン関数"""
    print("YOLOX + ByteTrack 統合動作テスト開始\n")
    
    tests = [
        ("設定ファイル", test_config_all),
        ("YOLOX基本動作", test_yolox_basic),
        ("GPU メモリ", test_gpu_memory),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"テスト: {test_name}")
        print(f"{'='*50}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name}テスト中にエラー: {e}")
            results[test_name] = False
    
    # 結果サマリー
    print(f"\n{'='*50}")
    print("テスト結果サマリー")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"\n成功: {passed}/{total} ({pass_rate:.1f}%)")
    
    if pass_rate >= 90:
        print("🎉 統合テスト成功！システムは正常に動作しています。")
        return 0
    elif pass_rate >= 70:
        print("⚠ 部分的成功。いくつかの問題がありますが基本機能は動作しています。")
        return 0
    else:
        print("❌ 統合テスト失敗。重大な問題があります。")
        return 1

if __name__ == "__main__":
    sys.exit(main())