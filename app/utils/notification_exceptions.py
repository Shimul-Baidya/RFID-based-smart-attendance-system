class NotificationError(Exception):
    """Base exception for notification-related failures."""


class DuplicateNotificationError(NotificationError):
    """Raised when a notification already exists for this attendance record."""


class NotificationDeliveryError(NotificationError):
    """Raised when a notification could not be created or delivered."""