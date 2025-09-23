"""Download history tracking using SQLite.

This module records successful downloads to avoid duplicates and provide
basic analytics (counts, last downloaded items).
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


HISTORY_DIR = Path.home() / ".youtube-extractor"
HISTORY_DB_PATH = HISTORY_DIR / "history.db"


def _ensure_history_dir() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class DownloadRecord:
    video_id: str
    title: str
    file_path: str
    downloaded_at: datetime


class DownloadHistory:
    """Lightweight wrapper around SQLite for download history management."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        _ensure_history_dir()
        self.db_path = Path(db_path) if db_path else HISTORY_DB_PATH
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path.as_posix())

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    downloaded_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_downloads_video_id ON downloads(video_id)"
            )
            conn.commit()

    def add_download(self, video_id: str, title: str, file_path: str) -> bool:
        """Track a successful download. Returns True if recorded, False if duplicate."""
        ts = datetime.utcnow().isoformat()
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO downloads (video_id, title, file_path, downloaded_at) VALUES (?, ?, ?, ?)",
                    (video_id, title, file_path, ts),
                )
                conn.commit()
                # Check if row was inserted
                cur = conn.execute("SELECT changes()")
                inserted = cur.fetchone()[0] or 0
                return inserted > 0
        except sqlite3.Error:
            return False

    def is_already_downloaded(self, video_id: str) -> bool:
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "SELECT 1 FROM downloads WHERE video_id = ? LIMIT 1",
                    (video_id,),
                )
                return cur.fetchone() is not None
        except sqlite3.Error:
            return False

    def recent_downloads(self, limit: int = 20) -> List[DownloadRecord]:
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    """
                    SELECT video_id, title, file_path, downloaded_at
                    FROM downloads
                    ORDER BY downloaded_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                return [
                    DownloadRecord(
                        video_id=row[0],
                        title=row[1],
                        file_path=row[2],
                        downloaded_at=datetime.fromisoformat(row[3]),
                    )
                    for row in rows
                ]
        except sqlite3.Error:
            return []

    def stats(self) -> Tuple[int, Optional[datetime]]:
        """Return total downloads count and last download timestamp (UTC)."""
        try:
            with self._connect() as conn:
                cur = conn.execute("SELECT COUNT(*), MAX(downloaded_at) FROM downloads")
                count, last_ts = cur.fetchone()
                last_dt = datetime.fromisoformat(last_ts) if last_ts else None
                return int(count or 0), last_dt
        except sqlite3.Error:
            return 0, None


