from __future__ import annotations
import datetime
from zoneinfo import ZoneInfo
from typing import Optional

def now_utc() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)

def ensure_aware(dt: datetime.datetime, tz: Optional[ZoneInfo]=None) -> datetime.datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz or datetime.timezone.utc)
    return dt

def to_timezone(dt: datetime.datetime, tz_name: str) -> datetime.datetime:
    tz = ZoneInfo(tz_name)
    dt = ensure_aware(dt, datetime.timezone.utc)
    return dt.astimezone(tz)

def convert_time_string(time_str: str, from_tz: str, to_tz: str) -> str:
    """Convert an ISO-like time string from one timezone to another and return ISO string in target tz."""
    # parse
    try:
        if time_str.endswith('Z'):
            dt = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        else:
            dt = datetime.datetime.fromisoformat(time_str)
    except Exception:
        # fallback: naive parse
        dt = datetime.datetime.fromisoformat(time_str)

    src = ZoneInfo(from_tz)
    tgt = ZoneInfo(to_tz)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=src)
    return dt.astimezone(tgt).isoformat()

def what_is_timezone_in_nairobi(target_tz_name: str, reference: Optional[datetime.datetime]=None) -> str:
    """Return the current time in `target_tz_name` expressed in Nairobi local time.

    Example: caller asks 'what is London time in Nairobi' -> returns the time in Nairobi when it's now in London.
    """
    nairobi = ZoneInfo('Africa/Nairobi')
    target = ZoneInfo(target_tz_name)
    now_ref = reference or datetime.datetime.now(tz=datetime.timezone.utc)
    # current time in target tz
    target_now = now_ref.astimezone(target)
    # represent that target time as seen in Nairobi
    nairobi_equiv = target_now.astimezone(nairobi)
    return nairobi_equiv.isoformat()
