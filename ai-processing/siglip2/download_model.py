#!/usr/bin/env python3
"""
SigLIP2モデルダウンロードスクリプト
事前にモデルをダウンロードしてキャッシュします
"""

import os
from pathlib import Path


def download_siglip2_model():
    """SigLIP2モデルをダウンロード"""
    from transformers import AutoModel, AutoProcessor

    model_name = "google/siglip2-base-patch16-256"
    cache_dir = os.environ.get("HF_HOME", "/workspace/models/huggingface")

    print(f"モデル: {model_name}")
    print(f"キャッシュディレクトリ: {cache_dir}")
    print("ダウンロード開始...")

    # プロセッサのダウンロード
    print("プロセッサをダウンロード中...")
    processor = AutoProcessor.from_pretrained(
        model_name,
        cache_dir=cache_dir
    )
    print("プロセッサのダウンロード完了")

    # モデルのダウンロード
    print("モデルをダウンロード中...")
    model = AutoModel.from_pretrained(
        model_name,
        cache_dir=cache_dir
    )
    print("モデルのダウンロード完了")

    print(f"\nダウンロード完了: {model_name}")
    print(f"保存先: {cache_dir}")


def main():
    """メイン実行関数"""
    print("=" * 50)
    print("SigLIP2 モデルダウンローダー")
    print("=" * 50)

    download_siglip2_model()

    print("\n全てのダウンロードが完了しました")


if __name__ == "__main__":
    main()
