#!/usr/bin/env python3
"""
SAM3モデルダウンロードスクリプト
事前にモデルをダウンロードしてキャッシュします

注意: SAM3はゲート付きモデルのため、HF_TOKENが必要です
"""

import os
from pathlib import Path


def check_token():
    """HF_TOKENの確認"""
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("エラー: HF_TOKENが設定されていません")
        print("SAM3はゲート付きモデルのため、Hugging Faceトークンが必要です")
        print("")
        print("設定方法:")
        print("1. https://huggingface.co/settings/tokens でトークンを取得")
        print("2. https://huggingface.co/facebook/sam3 でモデルへのアクセスをリクエスト")
        print("3. export HF_TOKEN=your_token_here を実行")
        print("   または .env ファイルに HF_TOKEN=your_token_here を記載")
        return None
    return token


def download_sam3_model():
    """SAM3モデルをダウンロード"""
    from transformers import AutoModel, AutoProcessor

    token = check_token()
    if not token:
        return False

    model_name = "facebook/sam3"
    cache_dir = os.environ.get("HF_HOME", "/workspace/models/huggingface")

    print(f"モデル: {model_name}")
    print(f"キャッシュディレクトリ: {cache_dir}")
    print("ダウンロード開始...")

    try:
        # プロセッサのダウンロード
        print("プロセッサをダウンロード中...")
        processor = AutoProcessor.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            token=token
        )
        print("プロセッサのダウンロード完了")

        # モデルのダウンロード
        print("モデルをダウンロード中...")
        model = AutoModel.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            token=token
        )
        print("モデルのダウンロード完了")

        print(f"\nダウンロード完了: {model_name}")
        print(f"保存先: {cache_dir}")
        return True

    except Exception as e:
        print(f"ダウンロードエラー: {e}")
        print("")
        print("トラブルシューティング:")
        print("1. HF_TOKENが正しいか確認")
        print("2. https://huggingface.co/facebook/sam3 でアクセス許可を取得済みか確認")
        return False


def main():
    """メイン実行関数"""
    print("=" * 50)
    print("SAM3 モデルダウンローダー")
    print("=" * 50)

    success = download_sam3_model()

    if success:
        print("\n全てのダウンロードが完了しました")
    else:
        print("\nダウンロードに失敗しました")
        exit(1)


if __name__ == "__main__":
    main()
