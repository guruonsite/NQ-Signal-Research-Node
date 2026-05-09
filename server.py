import os
import time
from typing import Any, Dict

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("GuruOnSite NQ Signal MCP")

LATEST_URL = os.getenv("GURU_SIGNAL_LATEST_URL", "").strip()
DAY_URL = os.getenv("GURU_SIGNAL_DAY_URL", "").strip()
TOKEN = os.getenv("GURU_SIGNAL_TOKEN", "").strip()
TIMEOUT = float(os.getenv("GURU_REQUEST_TIMEOUT", "3"))
DEMO_MODE = os.getenv("GURU_DEMO_MODE", "false").lower() == "true"


def _demo_latest() -> Dict[str, Any]:
    return {
        "ok": True,
        "demo": True,
        "source": "guruonsite_signal_mcp",
        "signal": {
            "signal_id": "DEMO-NQ-0001",
            "symbol": "/NQ",
            "side": "LONG",
            "strategy": "bullbearflag3",
            "entry": 27896.75,
            "stop": 27876.75,
            "target": 27911.75,
            "risk_ticks": 80,
            "target_ticks": 60,
            "confidence": 82,
            "verdict": "demo",
            "status": "demo",
            "timestamp_utc": "2026-05-08T00:00:00Z",
            "chartshot_url": None,
            "disclaimer": "Demo data only. Not financial advice."
        }
    }


def _pick(raw: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = raw.get(key)
        if value not in (None, ""):
            return value
    return None


def _detect_side(value: Any) -> Any:
    text = str(value or "").upper()
    if "LONG" in text or "BULL" in text or "BUY" in text:
        return "LONG"
    if "SHORT" in text or "BEAR" in text or "SELL" in text:
        return "SHORT"
    return text or None


def _normalize_signal(raw: Any) -> Dict[str, Any]:
    """
    Converts watcher/supervisor JSON into a stable agent-friendly payload.
    Keep raw included so we can debug field mapping without losing information.
    """
    if isinstance(raw, list):
        raw = raw[-1] if raw else {}

    if not isinstance(raw, dict):
        raw = {"raw_value": raw}

    side = _detect_side(_pick(raw, "side", "direction", "signal", "bias", "alert", "text"))

    normalized = {
        "signal_id": _pick(raw, "signal_id", "id", "alert_id", "uuid"),
        "symbol": _pick(raw, "symbol", "instrument", "ticker") or "/NQ",
        "side": side,
        "strategy": _pick(raw, "strategy", "script", "study", "source_strategy") or "unknown",
        "entry": _pick(raw, "entry", "entry_price", "price", "mark", "alert_price"),
        "stop": _pick(raw, "stop", "stop_loss", "sl"),
        "target": _pick(raw, "target", "take_profit", "tp"),
        "risk_ticks": _pick(raw, "risk_ticks", "stop_ticks"),
        "target_ticks": _pick(raw, "target_ticks", "take_profit_ticks"),
        "confidence": _pick(raw, "confidence", "score", "confidence_score"),
        "verdict": _pick(raw, "verdict", "supervisor_verdict", "decision"),
        "status": _pick(raw, "status", "state") or "active",
        "timestamp_utc": _pick(raw, "timestamp_utc", "utc", "time_utc", "created_utc"),
        "timestamp_local": _pick(raw, "timestamp_local", "display_time", "time", "created_at"),
        "chartshot_url": _pick(raw, "chartshot_url", "screenshot_url", "image_url", "chart_url"),
        "raw": raw,
        "disclaimer": "For research, journaling, and educational use only. Not financial advice."
    }

    return normalized


def _get_json(url: str) -> Any:
    if not url:
        raise RuntimeError("Feed URL is not configured.")

    headers = {"User-Agent": "GuruOnSiteSignalMCP/0.1"}
    params = {}
    if TOKEN:
        params["token"] = TOKEN

    response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_latest_nq_signal() -> Dict[str, Any]:
    """
    Return the latest GuruOnSite NQ signal in a stable AI-agent-friendly format.
    Read-only. Does not place trades.
    """
    if DEMO_MODE:
        return _demo_latest()

    raw = _get_json(LATEST_URL)
    return {
        "ok": True,
        "source": "guruonsite.net",
        "received_at_unix": int(time.time()),
        "signal": _normalize_signal(raw)
    }


@mcp.tool()
def get_signals_today(limit: int = 25) -> Dict[str, Any]:
    """
    Return recent GuruOnSite NQ signals for today/history.
    Read-only. Does not place trades.
    """
    if DEMO_MODE:
        demo = _demo_latest()["signal"]
        return {"ok": True, "demo": True, "count": 1, "signals": [demo]}

    raw = _get_json(DAY_URL)

    if isinstance(raw, dict):
        items = raw.get("signals") or raw.get("items") or raw.get("data") or [raw]
    elif isinstance(raw, list):
        items = raw
    else:
        items = []

    safe_limit = max(1, min(int(limit), 200))
    items = items[-safe_limit:]
    signals = [_normalize_signal(item) for item in items]

    return {
        "ok": True,
        "source": "guruonsite.net",
        "count": len(signals),
        "signals": signals
    }


@mcp.tool()
def get_feed_status() -> Dict[str, Any]:
    """
    Check whether the GuruOnSite signal feed is reachable.
    """
    if DEMO_MODE:
        return {"ok": True, "demo": True, "message": "Demo mode enabled."}

    try:
        raw = _get_json(LATEST_URL)
        return {
            "ok": True,
            "latest_url_configured": bool(LATEST_URL),
            "day_url_configured": bool(DAY_URL),
            "token_present": bool(TOKEN),
            "latest_payload_type": type(raw).__name__,
            "message": "Feed reachable."
        }
    except Exception as exc:
        return {
            "ok": False,
            "latest_url_configured": bool(LATEST_URL),
            "day_url_configured": bool(DAY_URL),
            "token_present": bool(TOKEN),
            "error": str(exc)
        }


if __name__ == "__main__":
    mcp.run()
