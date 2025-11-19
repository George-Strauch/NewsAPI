# Usage:
#   iface = ArticleInterface.get()
#   iface.article_store.some_method()

import threading
import time

from news_base.database.sources_db import SourceStorePG
from news_base.database.domain_db import DomainStorePG


class SourceInterface:
    """
    Thread-safe singleton wrapper for ArticleStorePG.
    Ensures that only one ArticleStorePG instance is created per process.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        # Prevent direct construction if instance already exists
        if SourceInterface._instance is not None:
            raise RuntimeError("Use ArticleInterface.get() instead of direct instantiation.")

        self.source_store = SourceStorePG()
        self.domain_store = DomainStorePG()
        self.domain_counts = 67
        self.sitemap_counts = 67
        self.last_count_update = 0
        self.count_update_interval = 60 * 60
        self.get_domain_counts(force_get=True)

    def get_domain_counts(self, force_get=False):
        if time.time() - self.last_count_update > self.count_update_interval or force_get:
            print("updating counts")
            delta = time.time() - self.last_count_update
            print(f"source count delta: {delta}")
            domain_counts = self.domain_store.count_all()
            self.last_count_update = time.time()
            self.domain_counts = domain_counts
            print("done updating counts")

        return self.domain_counts

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
