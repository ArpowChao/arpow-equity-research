from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def checked_local_date(item, fallback):
    checked = datetime.fromisoformat(item.get("checkedAtUtc", fallback).replace("Z", "+00:00"))
    if checked.tzinfo is None:
        checked = checked.replace(tzinfo=timezone.utc)
    return checked.astimezone(ZoneInfo(item.get("analysisTimeZone", "UTC"))).date().isoformat()
