# Usage:
#   iface = ArticleInterface.get()
#   iface.article_store.some_method()

import threading
import time

from news_base.database.news_db import ArticleStorePG


class ArticleInterface:
    """
    Thread-safe singleton wrapper for ArticleStorePG.
    Ensures that only one ArticleStorePG instance is created per process.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # Prevent direct construction if instance already exists
        if ArticleInterface._instance is not None:
            raise RuntimeError("Use ArticleInterface.get() instead of direct instantiation.")

        self.article_store = ArticleStorePG()
        self.article_count = 67
        self.last_count_update = 0
        self.count_update_interval = 60 * 60
        self.get_counts(force_get=True)

    def get_counts(self, force_get=False):
        delta = time.time() - self.last_count_update
        print(f"article count delta: {delta}")
        if time.time() - self.last_count_update > self.count_update_interval or force_get:
            print("updating counts")
            counts = self.article_store.counts()
            self.article_count = counts['total']
        return self.article_count

    @classmethod
    def get(cls):
        """
        Returns the singleton instance, constructing it on first access.
        Thread-safe.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
