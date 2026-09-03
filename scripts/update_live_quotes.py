#!/usr/bin/env python3
"""Build a same-origin delayed quote snapshot for the static Pages site."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "src" / "data" / "reports.generated.json"
OUTPUT = ROOT / "public" / "data" / "live-quotes.json"
ENDPOINTS = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
    "https://query2.finance.yahoo.com/v8/finance/chart/{ticker}",
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ArpowResearch/1.0)",
    "Accept": "application/json,text/plain,*/*",
}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def session_for(ts: int, tz_name: str) -> str:
    local = datetime.fromtimestamp(ts, ZoneInfo(tz_name))
    minutes = local.hour * 60 + local.minute
    if 240 <= minutes < 570:
        return "pre-market"
    if 570 <= minutes < 960:
        return "regular"
    if 960 <= minutes <= 1200:
        return "post-market"
    return "closed"


def collect_quote(ticker: str) -> dict:
    query = urllib.parse.urlencode({"range": "1d", "interval": "1m", "includePrePost": "true"})
    last_error: Exception | None = None
    for endpoint in ENDPOINTS:
        try:
            payload = fetch_json(f"{endpoint.format(ticker=urllib.parse.quote(ticker))}?{query}")
            result = payload["chart"]["result"][0]
            meta = result["meta"]
            timestamps = result.get("timestamp") or []
            closes = result.get("indicators", {}).get("quote", [{}])[0].get("close") or []
            observed = [(int(ts), float(price)) for ts, price in zip(timestamps, closes) if price is not None]
            if not observed:
                raise ValueError("no observed prices")
            latest_ts, latest_price = observed[-1]
            tz_name = meta.get("exchangeTimezoneName") or "America/New_York"
            phase = session_for(latest_ts, tz_name)
            regular_price = float(meta.get("regularMarketPrice") or latest_price)
            previous_close = meta.get("previousClose")
            if previous_close is None:
                previous_close = meta.get("chartPreviousClose")
            if phase in {"pre-market", "post-market", "closed"}:
                reference = regular_price
            else:
                reference = float(previous_close) if previous_close else regular_price
            change = latest_price - reference
            change_percent = (change / reference * 100) if reference else 0.0
            return {
                "ticker": ticker,
                "price": round(latest_price, 4),
                "change": round(change, 4),
                "changePercent": round(change_percent, 4),
                "phase": phase,
                "observedAt": datetime.fromtimestamp(latest_ts, timezone.utc).isoformat().replace("+00:00", "Z"),
                "exchangeTimezone": tz_name,
                "regularMarketPrice": round(regular_price, 4),
                "referencePrice": round(reference, 4),
                "currency": meta.get("currency") or "USD",
                "exchange": meta.get("fullExchangeName") or meta.get("exchangeName") or "",
                "source": "Yahoo Finance chart API",
            }
        except (KeyError, IndexError, TypeError, ValueError, OSError, urllib.error.URLError) as exc:
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"{ticker}: {last_error}")


def main() -> None:
    reports = json.loads(REPORTS.read_text(encoding="utf-8"))
    tickers = sorted({str(report["ticker"]).upper() for report in reports})
    quotes: dict[str, dict] = {}
    failures: dict[str, str] = {}
    # Quote providers can throttle or stall individual symbols. A bounded pool
    # keeps the scheduled Pages build below its 15-minute cadence without
    # creating an unbounded burst of requests.
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(collect_quote, ticker): ticker for ticker in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                quotes[ticker] = future.result()
                print(f"updated {ticker}")
            except RuntimeError as exc:
                failures[ticker] = str(exc)
                print(f"failed {ticker}: {exc}")
    if not quotes:
        raise SystemExit("no quotes collected")
    payload = {
        "fetchedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "updatePolicy": "Scheduled snapshot; normally refreshed about every 15 minutes during U.S. extended trading hours on weekdays.",
        "quotes": quotes,
        "unavailable": sorted(failures),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(quotes)}/{len(tickers)} quotes -> {OUTPUT}")
    if failures:
        print("partial failures:", ", ".join(sorted(failures)))


if __name__ == "__main__":
    main()
