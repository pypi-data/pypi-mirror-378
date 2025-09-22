"""
Token Refresh Observer Pattern

This module provides the observer pattern implementation for token refresh notifications.
When tokens are refreshed, all registered observers are automatically notified with the new token.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import logging
from ..config.main import RevosMainConfig

logger = logging.getLogger(__name__)


class TokenRefreshObserver(ABC):
    """
    Abstract base class for objects that need to be notified when tokens are refreshed.
    
    This interface allows any object to receive notifications when authentication tokens
    are refreshed, enabling automatic updates without manual intervention.
    """
    
    @abstractmethod
    def on_token_refreshed(self, new_token: str) -> None:
        """
        Called when a new authentication token is available.
        
        Args:
            new_token: The new authentication token that should be used
        """
        pass


class TokenRefreshNotifier:
    """
    Manages a list of observers and notifies them when tokens are refreshed.
    
    This class implements the observer pattern for token refresh notifications,
    allowing multiple objects to be automatically updated when new tokens are available.
    """
    
    def __init__(self):
        """Initialize the notifier with an empty list of observers."""
        self._observers: List[TokenRefreshObserver] = []
        self._lock = None
        
        # Import threading here to avoid circular imports
        try:
            import threading
            self._lock = threading.Lock()
        except ImportError:
            # Threading not available, proceed without lock
            pass
    
    def add_observer(self, observer: TokenRefreshObserver) -> None:
        """
        Add an observer to the notification list.
        
        Args:
            observer: The observer to add
            
        Raises:
            ValueError: If observer is None or already registered
        """
        if observer is None:
            raise ValueError("Observer cannot be None")
        
        if observer in self._observers:
            logger.warning(f"Observer {observer} is already registered")
            return
        
        if self._lock:
            with self._lock:
                self._observers.append(observer)
        else:
            self._observers.append(observer)
        
        logger.debug(f"Added observer {type(observer).__name__}")
    
    def remove_observer(self, observer: TokenRefreshObserver) -> None:
        """
        Remove an observer from the notification list.
        
        Args:
            observer: The observer to remove
        """
        if self._lock:
            with self._lock:
                try:
                    self._observers.remove(observer)
                    logger.debug(f"Removed observer {type(observer).__name__}")
                except ValueError:
                    logger.warning(f"Observer {observer} was not in the list")
        else:
            try:
                self._observers.remove(observer)
                logger.debug(f"Removed observer {type(observer).__name__}")
            except ValueError:
                logger.warning(f"Observer {observer} was not in the list")
    
    def notify_observers(self, new_token: str) -> None:
        """
        Notify all registered observers with the new token.
        
        Args:
            new_token: The new authentication token to send to observers
        """
        if not self._observers:
            logger.debug("No observers to notify")
            return
        
        logger.info(f"Notifying {len(self._observers)} observers with new token")
        
        # Create a copy of observers list to avoid modification during iteration
        observers_to_notify = self._observers.copy() if not self._lock else list(self._observers)
        
        for observer in observers_to_notify:
            try:
                observer.on_token_refreshed(new_token)
                logger.debug(f"Successfully notified observer {type(observer).__name__}")
            except Exception as e:
                logger.error(f"Failed to notify observer {type(observer).__name__}: {e}")
                logger.error(f"Observer notification traceback: {e}")
    
    def get_observer_count(self) -> int:
        """
        Get the number of registered observers.
        
        Returns:
            int: Number of registered observers
        """
        return len(self._observers)
    
    def clear_observers(self) -> None:
        """Remove all observers from the notification list."""
        if self._lock:
            with self._lock:
                self._observers.clear()
        else:
            self._observers.clear()
        
        logger.debug("Cleared all observers")


# Global notifier instance for automatic registration
_global_notifier: Optional[TokenRefreshNotifier] = None
# Global config instance for extractors to use
_global_config: Optional[RevosMainConfig] = None
# Global TokenManager instance for direct token access
_global_token_manager: Optional['TokenManager'] = None


def get_global_notifier() -> TokenRefreshNotifier:
    """
    Get the global token refresh notifier instance.
    
    Returns:
        TokenRefreshNotifier: The global notifier instance
    """
    global _global_notifier
    if _global_notifier is None:
        _global_notifier = TokenRefreshNotifier()
    return _global_notifier


def set_global_notifier(notifier: TokenRefreshNotifier) -> None:
    """
    Set the global token refresh notifier instance.
    
    Args:
        notifier: The notifier instance to use globally
    """
    global _global_notifier
    _global_notifier = notifier


def register_observer(observer: TokenRefreshObserver) -> None:
    """
    Register an observer with the global notifier.
    
    Args:
        observer: The observer to register
    """
    import logging
    logger = logging.getLogger(__name__)
    
    notifier = get_global_notifier()
    notifier.add_observer(observer)
    
    # If a global TokenManager is available, provide token immediately to new observer
    global_token_manager = get_global_token_manager()
    if global_token_manager is not None:
        try:
            # Get current token and provide it directly to the new observer
            token = global_token_manager.get_token()
            if token:
                observer.on_token_refreshed(token)
                logger.info("Provided current token to new observer immediately")
        except Exception as e:
            logger.warning(f"Failed to provide token to new observer: {e}")


def unregister_observer(observer: TokenRefreshObserver) -> None:
    """
    Unregister an observer from the global notifier.
    
    Args:
        observer: The observer to unregister
    """
    notifier = get_global_notifier()
    notifier.remove_observer(observer)


def notify_all_observers(new_token: str) -> None:
    """
    Notify all observers registered with the global notifier.
    
    Args:
        new_token: The new authentication token
    """
    notifier = get_global_notifier()
    notifier.notify_observers(new_token)


def set_global_config(config: Optional[RevosMainConfig]) -> None:
    """
    Set the global configuration that extractors should use.
    
    Args:
        config: The configuration instance to use globally, or None to clear
    """
    global _global_config
    _global_config = config
    if config is not None:
        logger.info("Global configuration set for extractors")
    else:
        logger.info("Global configuration cleared")


def get_global_config() -> Optional[RevosMainConfig]:
    """
    Get the global configuration instance.
    
    Returns:
        RevosMainConfig or None: The global configuration instance
    """
    return _global_config


def set_global_token_manager(token_manager: 'TokenManager') -> None:
    """
    Set the global TokenManager instance for direct token access.
    
    Args:
        token_manager: The TokenManager instance to use globally
    """
    global _global_token_manager
    _global_token_manager = token_manager
    logger.info("Global TokenManager set for direct token access")


def get_global_token_manager() -> Optional['TokenManager']:
    """
    Get the global TokenManager instance.
    
    Returns:
        TokenManager or None: The global TokenManager instance
    """
    return _global_token_manager
