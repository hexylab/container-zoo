#!/usr/bin/env python3
"""
ファイル・ディレクトリ操作ユーティリティ
"""

import os
import json
import shutil
from pathlib import Path
from typing import Union, Dict, Any, Optional
import logging


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    ディレクトリが存在しない場合は作成する
    
    Args:
        path: ディレクトリパス
        
    Returns:
        Path: 作成されたディレクトリのPathオブジェクト
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_remove(path: Union[str, Path]) -> bool:
    """
    安全にファイル・ディレクトリを削除
    
    Args:
        path: 削除対象のパス
        
    Returns:
        bool: 削除成功可否
    """
    path = Path(path)
    try:
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        return True
    except (OSError, PermissionError) as e:
        logging.warning(f"削除失敗: {path}, エラー: {e}")
        return False


def get_file_size(path: Union[str, Path]) -> int:
    """
    ファイルサイズを取得（バイト単位）
    
    Args:
        path: ファイルパス
        
    Returns:
        int: ファイルサイズ（バイト）
    """
    return Path(path).stat().st_size if Path(path).exists() else 0


def format_file_size(size_bytes: int) -> str:
    """
    ファイルサイズを読みやすい形式に変換
    
    Args:
        size_bytes: サイズ（バイト）
        
    Returns:
        str: フォーマット済みサイズ
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def save_json(data: Dict[str, Any], path: Union[str, Path], indent: int = 2) -> bool:
    """
    JSONファイルを安全に保存
    
    Args:
        data: 保存するデータ
        path: 保存先パス
        indent: インデント数
        
    Returns:
        bool: 保存成功可否
    """
    path = Path(path)
    ensure_dir(path.parent)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, default=str)
        return True
    except (OSError, TypeError) as e:
        logging.error(f"JSON保存失敗: {path}, エラー: {e}")
        return False


def load_json(path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """
    JSONファイルを安全に読み込み
    
    Args:
        path: JSONファイルパス
        
    Returns:
        Optional[Dict]: 読み込まれたデータ、失敗時はNone
    """
    path = Path(path)
    
    if not path.exists():
        logging.warning(f"JSONファイルが存在しません: {path}")
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logging.error(f"JSON読み込み失敗: {path}, エラー: {e}")
        return None


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """
    ファイルを安全にコピー
    
    Args:
        src: コピー元
        dst: コピー先
        
    Returns:
        bool: コピー成功可否
    """
    src, dst = Path(src), Path(dst)
    
    if not src.exists():
        logging.error(f"コピー元ファイルが存在しません: {src}")
        return False
    
    ensure_dir(dst.parent)
    
    try:
        shutil.copy2(src, dst)
        return True
    except (OSError, PermissionError) as e:
        logging.error(f"ファイルコピー失敗: {src} -> {dst}, エラー: {e}")
        return False


def get_available_filename(base_path: Union[str, Path], extension: str = "") -> Path:
    """
    利用可能なファイル名を生成（連番付き）
    
    Args:
        base_path: ベースとなるファイルパス
        extension: 拡張子
        
    Returns:
        Path: 利用可能なファイルパス
    """
    base_path = Path(base_path)
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    
    # 拡張子を処理
    if extension:
        base_name = base_path.stem
        base_dir = base_path.parent
        final_ext = extension
    else:
        base_name = base_path.stem
        base_dir = base_path.parent
        final_ext = base_path.suffix
    
    # ベースファイル名で試行
    candidate = base_dir / f"{base_name}{final_ext}"
    if not candidate.exists():
        return candidate
    
    # 連番を追加して検索
    counter = 1
    while True:
        candidate = base_dir / f"{base_name}_{counter:03d}{final_ext}"
        if not candidate.exists():
            return candidate
        counter += 1
        
        # 無限ループ防止
        if counter > 9999:
            raise RuntimeError("利用可能なファイル名が見つかりません")


def cleanup_old_files(directory: Union[str, Path], 
                     pattern: str = "*", 
                     max_age_days: int = 7,
                     max_count: int = 100) -> int:
    """
    古いファイルを削除（日数またはファイル数制限）
    
    Args:
        directory: 対象ディレクトリ
        pattern: ファイルパターン
        max_age_days: 最大保持日数
        max_count: 最大保持ファイル数
        
    Returns:
        int: 削除されたファイル数
    """
    directory = Path(directory)
    if not directory.exists():
        return 0
    
    import time
    from datetime import datetime, timedelta
    
    files = list(directory.glob(pattern))
    if not files:
        return 0
    
    # 日数制限での削除
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    deleted_count = 0
    
    for file_path in files:
        if file_path.stat().st_mtime < cutoff_time:
            if safe_remove(file_path):
                deleted_count += 1
    
    # ファイル数制限での削除
    remaining_files = [f for f in files if f.exists()]
    if len(remaining_files) > max_count:
        # 更新日時でソート
        remaining_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        files_to_delete = remaining_files[max_count:]
        
        for file_path in files_to_delete:
            if safe_remove(file_path):
                deleted_count += 1
    
    return deleted_count