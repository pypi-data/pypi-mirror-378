"""Simple analytics from download history."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .history import DownloadHistory


def generate_report(limit: int = 100) -> Dict[str, Any]:
    history = DownloadHistory()
    total, last_dt = history.stats()
    recents = history.recent_downloads(limit=limit)

    # Basic top titles (by occurrences) and formats
    titles = [r.title for r in recents]
    paths = [r.file_path for r in recents]
    exts = [Path(p).suffix.lower().lstrip('.') for p in paths]

    report = {
        'total_downloads': total,
        'last_download_utc': last_dt.isoformat() if last_dt else None,
        'recent_count': len(recents),
        'top_titles': Counter(titles).most_common(5),
        'formats': Counter(exts),
    }
    return report


