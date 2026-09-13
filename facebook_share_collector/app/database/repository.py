import sqlite3
import os
import logging
from typing import List, Optional
from app.models.share_profile import ShareProfile
from app.models.collection_session import CollectionSession

logger = logging.getLogger(__name__)

class DatabaseRepository:
    def __init__(self, db_path: str = "data/facebook_shares.sqlite"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS collection_sessions (
                        id TEXT PRIMARY KEY,
                        start_time TEXT,
                        end_time TEXT,
                        status TEXT,
                        total_profiles INTEGER,
                        total_scrolls INTEGER
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS profiles (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        profile_url TEXT,
                        share_url TEXT,
                        source TEXT,
                        confidence REAL,
                        first_seen_at TEXT,
                        last_seen_at TEXT,
                        session_id TEXT,
                        FOREIGN KEY(session_id) REFERENCES collection_sessions(id)
                    )
                """)
                # Create indexes to speed up deduplication searches
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_url ON profiles(profile_url)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles(name)")
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")

    def create_session(self, session: CollectionSession):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO collection_sessions (id, start_time, end_time, status, total_profiles, total_scrolls) VALUES (?, ?, ?, ?, ?, ?)",
                    (session.id, session.start_time, session.end_time, session.status, session.total_profiles, session.total_scrolls)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to create session in db: {e}")

    def update_session(self, session: CollectionSession):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE collection_sessions SET end_time = ?, status = ?, total_profiles = ?, total_scrolls = ? WHERE id = ?",
                    (session.end_time, session.status, session.total_profiles, session.total_scrolls, session.id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update session in db: {e}")

    def save_profile(self, profile: ShareProfile):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO profiles (id, name, profile_url, share_url, source, confidence, first_seen_at, last_seen_at, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (profile.id, profile.name, profile.profile_url, profile.share_url, profile.source, profile.confidence, profile.first_seen_at, profile.last_seen_at, profile.session_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to save profile in db: {e}")

    def update_profile_last_seen(self, profile_id: str, last_seen_at: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE profiles SET last_seen_at = ? WHERE id = ?", (last_seen_at, profile_id))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update profile last_seen in db: {e}")

    def get_all_profiles_for_session(self, session_id: str) -> List[ShareProfile]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM profiles WHERE session_id = ?", (session_id,))
                rows = cursor.fetchall()
                profiles = []
                for row in rows:
                    profiles.append(ShareProfile(
                        id=row[0], name=row[1], profile_url=row[2], share_url=row[3],
                        source=row[4], confidence=row[5], first_seen_at=row[6],
                        last_seen_at=row[7], session_id=row[8]
                    ))
                return profiles
        except sqlite3.Error as e:
            logger.error(f"Failed to get profiles for session: {e}")
            return []

    def get_sessions(self) -> List[CollectionSession]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM collection_sessions ORDER BY start_time DESC")
                rows = cursor.fetchall()
                sessions = []
                for row in rows:
                    sessions.append(CollectionSession(
                        id=row[0], start_time=row[1], end_time=row[2], status=row[3],
                        total_profiles=row[4], total_scrolls=row[5]
                    ))
                return sessions
        except sqlite3.Error as e:
            logger.error(f"Failed to get sessions: {e}")
            return []
