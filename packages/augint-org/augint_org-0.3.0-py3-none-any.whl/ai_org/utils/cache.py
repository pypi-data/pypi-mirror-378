"""Caching utilities for API responses."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional


class CacheManager:
    """Manages caching of API responses."""

    def __init__(self, cache_dir: Optional[Path] = None, ttl: int = 3600):
        """Initialize cache manager.

        Args:
            cache_dir: Directory for cache files (defaults to ~/.aillc/cache or /tmp in CI)
            ttl: Time-to-live for cache entries in seconds (default 1 hour)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        elif os.getenv("CI"):  # In CI environment
            self.cache_dir = Path("/tmp/.aillc/cache")
        else:
            self.cache_dir = Path.home() / ".aillc" / "cache"

        self.ttl = ttl
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # Can't create cache dir - will handle in get/set methods
            pass

    def _get_cache_key(self, namespace: str, key: str) -> str:
        """Generate cache key.

        Args:
            namespace: Cache namespace
            key: Key within namespace

        Returns:
            Hashed cache key
        """
        combined = f"{namespace}:{key}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _get_cache_path(self, namespace: str, key: str) -> Path:
        """Get path to cache file.

        Args:
            namespace: Cache namespace
            key: Key within namespace

        Returns:
            Path to cache file
        """
        cache_key = self._get_cache_key(namespace, key)
        return self.cache_dir / f"{namespace}_{cache_key}.json"

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get cached value.

        Args:
            namespace: Cache namespace
            key: Key within namespace

        Returns:
            Cached value or None if not found, expired, or on any error
        """
        try:
            cache_path = self._get_cache_path(namespace, key)

            if not cache_path.exists():
                return None  # Cache miss - caller should fetch

            with open(cache_path) as f:
                cache_data = json.load(f)

            # Check if expired
            if time.time() - cache_data["timestamp"] > self.ttl:
                try:
                    cache_path.unlink()  # Try to delete expired cache
                except (OSError, PermissionError):
                    pass  # Can't delete, but still return None
                return None  # Expired - caller should fetch

            return cache_data["value"]

        except (OSError, PermissionError, json.JSONDecodeError, KeyError):
            # Can't read/write cache or invalid data - continue without it
            return None

    def set(self, namespace: str, key: str, value: Any) -> None:
        """Set cached value.

        Args:
            namespace: Cache namespace
            key: Key within namespace
            value: Value to cache
        """
        try:
            cache_path = self._get_cache_path(namespace, key)

            # Ensure directory exists
            cache_path.parent.mkdir(parents=True, exist_ok=True)

            cache_data = {
                "timestamp": time.time(),
                "value": value,
            }

            with open(cache_path, "w") as f:
                json.dump(cache_data, f, default=str)
        except (OSError, PermissionError):
            # Can't write cache - continue without it
            pass

    def clear(self, namespace: Optional[str] = None) -> None:
        """Clear cache.

        Args:
            namespace: Clear specific namespace or all if None
        """
        try:
            if namespace:
                # Clear specific namespace
                for cache_file in self.cache_dir.glob(f"{namespace}_*.json"):
                    try:
                        cache_file.unlink()
                    except (OSError, PermissionError):
                        pass  # Skip files we can't delete
            else:
                # Clear all cache
                for cache_file in self.cache_dir.glob("*.json"):
                    try:
                        cache_file.unlink()
                    except (OSError, PermissionError):
                        pass  # Skip files we can't delete
        except (OSError, PermissionError):
            # Can't access cache directory
            pass

    def get_or_compute(self, namespace: str, key: str, compute_fn: Callable[[], Any]) -> Any:
        """Get cached value or compute if not found.

        Args:
            namespace: Cache namespace
            key: Key within namespace
            compute_fn: Function to compute value if not cached

        Returns:
            Cached or computed value
        """
        value = self.get(namespace, key)

        if value is None:
            value = compute_fn()
            self.set(namespace, key, value)

        return value
