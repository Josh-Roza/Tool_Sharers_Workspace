from __future__ import annotations

import json
import math
import time
import urllib.parse
import urllib.request
from typing import Optional, Tuple

from django.conf import settings
from django.core.cache import cache

from .models import GeocodedAddress


NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_MIN_SECONDS_BETWEEN_REQUESTS = 1.1
NOMINATIM_THROTTLE_CACHE_KEY = "tool_sharers:nominatim:last_request_ts"


def normalize_query(query: str) -> str:
    return " ".join(query.strip().lower().split())


def _throttle_nominatim() -> None:
    """Throttle outbound calls to respect Nominatim usage expectations."""

    last_ts = cache.get(NOMINATIM_THROTTLE_CACHE_KEY)
    now = time.time()

    if last_ts is not None:
        elapsed = now - float(last_ts)
        remaining = NOMINATIM_MIN_SECONDS_BETWEEN_REQUESTS - elapsed
        if remaining > 0:
            # Keep this small; this is a user-facing request.
            time.sleep(min(remaining, 1.5))

    cache.set(NOMINATIM_THROTTLE_CACHE_KEY, time.time(), timeout=60)


def geocode_address(query: str) -> Optional[Tuple[float, float]]:
    query = normalize_query(query)
    if not query:
        return None

    cached = GeocodedAddress.objects.filter(query=query).only("latitude", "longitude").first()
    if cached:
        return (cached.latitude, cached.longitude)

    _throttle_nominatim()

    user_agent = getattr(settings, "GEOCODER_USER_AGENT", None) or "ToolSharers/1.0 (Django)"

    params = {
        "format": "json",
        "q": query,
        "limit": 1,
    }
    url = f"{NOMINATIM_SEARCH_URL}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            payload = resp.read().decode("utf-8")
    except Exception:
        return None

    try:
        data = json.loads(payload)
    except Exception:
        return None

    if not data:
        return None

    try:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
    except Exception:
        return None

    GeocodedAddress.objects.update_or_create(
        query=query,
        defaults={"latitude": lat, "longitude": lon},
    )

    return (lat, lon)


def haversine_miles(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lon1 = a
    lat2, lon2 = b

    r_miles = 3958.7613

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    sin_dphi = math.sin(d_phi / 2.0)
    sin_dlambda = math.sin(d_lambda / 2.0)

    h = sin_dphi * sin_dphi + math.cos(phi1) * math.cos(phi2) * sin_dlambda * sin_dlambda
    c = 2.0 * math.atan2(math.sqrt(h), math.sqrt(1.0 - h))

    return r_miles * c
