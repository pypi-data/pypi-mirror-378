"""Cache for tracking transport layer setup status"""

from typing import Dict, Optional, Set, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib


class TransportSetupCache:
    """
    Cache for tracking which transports have been set up for each account.
    
    The cache tracks:
    - Which transports were successfully set up
    - When they were last verified
    - Configuration hash to detect changes
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.syft/cache
        """
        self.cache_dir = cache_dir or (Path.home() / ".syft" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=24)
    
    def _get_cache_key(self, email: str, platform: str) -> str:
        """Generate a cache key for the given email and platform"""
        # Hash the email to avoid issues with special characters in filenames
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:12]
        return f"{platform}_{email_hash}"
    
    def _get_cache_file(self, email: str, platform: str) -> Path:
        """Get the cache file path for a specific email and platform"""
        cache_key = self._get_cache_key(email, platform)
        return self.cache_dir / f"{cache_key}_transport_setup.json"
    
    def _compute_config_hash(self, credentials_path: Optional[Path] = None) -> str:
        """
        Compute a hash of relevant configuration to detect changes.
        
        This helps invalidate cache if credentials or config changes.
        """
        parts = []
        
        # Include credentials file modification time if it exists
        if credentials_path and credentials_path.exists():
            parts.append(f"creds:{credentials_path.stat().st_mtime}")
        
        # Create a hash of all parts
        combined = "|".join(parts)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def get_setup_status(
        self, 
        email: str, 
        platform: str,
        credentials_path: Optional[Path] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached setup status for transports.
        
        Args:
            email: User's email address
            platform: Platform name (e.g., 'google_personal', 'google_org')
            credentials_path: Path to credentials file (for change detection)
            
        Returns:
            Dict with transport setup status or None if cache miss/expired
        """
        cache_file = self._get_cache_file(email, platform)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            last_verified = datetime.fromisoformat(cache_data['last_verified'])
            if datetime.now() - last_verified > self.cache_ttl:
                return None
            
            # Check if configuration has changed
            current_hash = self._compute_config_hash(credentials_path)
            if cache_data.get('config_hash') != current_hash:
                return None
            
            return cache_data
            
        except Exception:
            # If any error reading cache, treat as cache miss
            return None
    
    def save_setup_status(
        self,
        email: str,
        platform: str,
        configured_transports: Set[str],
        credentials_path: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save transport setup status to cache.
        
        Args:
            email: User's email address
            platform: Platform name
            configured_transports: Set of successfully configured transport names
            credentials_path: Path to credentials file
            metadata: Additional metadata to store
            
        Returns:
            True if saved successfully
        """
        cache_file = self._get_cache_file(email, platform)
        
        try:
            cache_data = {
                'email': email,
                'platform': platform,
                'configured_transports': list(configured_transports),
                'last_verified': datetime.now().isoformat(),
                'config_hash': self._compute_config_hash(credentials_path),
                'metadata': metadata or {}
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def invalidate(self, email: str, platform: str) -> bool:
        """
        Invalidate cache for a specific email and platform.
        
        Args:
            email: User's email address
            platform: Platform name
            
        Returns:
            True if cache was invalidated
        """
        cache_file = self._get_cache_file(email, platform)
        
        if cache_file.exists():
            try:
                cache_file.unlink()
                return True
            except Exception:
                pass
        
        return False
    
    def get_transport_last_verified(
        self, 
        email: str, 
        platform: str, 
        transport_name: str
    ) -> Optional[datetime]:
        """
        Get when a specific transport was last verified.
        
        Args:
            email: User's email address
            platform: Platform name
            transport_name: Name of the transport
            
        Returns:
            Datetime of last verification or None
        """
        status = self.get_setup_status(email, platform)
        
        if not status:
            return None
        
        if transport_name in status.get('configured_transports', []):
            return datetime.fromisoformat(status['last_verified'])
        
        return None
    
    def is_transport_setup_cached(
        self,
        email: str,
        platform: str,
        transport_name: str,
        credentials_path: Optional[Path] = None
    ) -> bool:
        """
        Check if a specific transport is marked as set up in cache.
        
        Args:
            email: User's email address
            platform: Platform name
            transport_name: Name of the transport
            credentials_path: Path to credentials file
            
        Returns:
            True if transport is set up according to cache
        """
        status = self.get_setup_status(email, platform, credentials_path)
        
        if not status:
            return False
        
        return transport_name in status.get('configured_transports', [])