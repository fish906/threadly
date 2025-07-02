from datetime import datetime, timedelta
from threadly.models import IPLog

def is_rate_limited(db, ip_address: str, limit: int = 2, window_minutes: int = 1) -> bool:
    """
    Returns True if the given IP has exceeded the allowed request limit in the time window.
    """
    time_window = datetime.now() - timedelta(minutes=window_minutes)
    count = db.query(IPLog).filter(
        IPLog.ip_address == ip_address,
        IPLog.created_at >= time_window
    ).count()

    return count >= limit