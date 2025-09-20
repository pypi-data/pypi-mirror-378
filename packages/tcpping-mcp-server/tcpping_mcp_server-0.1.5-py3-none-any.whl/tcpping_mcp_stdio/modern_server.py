"""Modern FastMCP-based TCP ping server using the latest FastMCP framework.

Merged: Core tcp ping scraping logic (formerly in tcpping_core.py) is now
embedded here for easier single-file debugging. The old module path still
exports run_test for backward compatibility.
"""
from __future__ import annotations
from fastmcp import FastMCP
import json, asyncio, math, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# --- Core constants & data models (migrated from tcpping_core.py) ---
PROGRESS_SELECTORS = {
    "progress_percent": "[ref=e78]",
    "fastest": "[ref=e1293]",
    "slowest": "[ref=e1294]",
    "domestic_avg": "[ref=e1295]",
    "foreign_avg": "[ref=e1296]",
}
OVERVIEW_ROWS = [
    ("e2932", "电信", ("e1299", "e1300", "e1302", "e1303", "e1305")),
    ("e2936", "联通", ("e2938", "e2939", "e2941", "e2942", "e2944")),
    ("e2945", "移动", ("e2947", "e2948", "e2950", "e2951", "e2953")),
    ("e2954", "多线", ("e1308", "e1309", "e1311", "e1312", "e1314")),
    ("e2958", "港澳台", ("e1317", "e1318", "e1320", "e1321", "e1323")),
    ("e2961", "海外", ("e1326", "e1327", "e1329", "e1330", "e1332")),
]
TABLE_BODY_SELECTOR = "[ref=e201]"

@dataclass
class OverviewEntry:
    provider: str
    fastest_node: Optional[str]
    fastest_ms: Optional[float]
    slowest_node: Optional[str]
    slowest_ms: Optional[float]
    average_ms: Optional[float]

@dataclass
class ProbeRow:
    provider: Optional[str]
    location: Optional[str]
    ip: Optional[str]
    ip_location: Optional[str]
    latency_ms: Optional[float]
    timeout: bool
    sponsor: Optional[str]

def _parse_latency(text: str):
    text = text.strip()
    if not text:
        return None, False
    if "超时" in text:
        return None, True
    import re
    m = re.search(r"(\d+(?:\.\d+)?)\s*ms", text)
    if m:
        return float(m.group(1)), False
    return None, False

async def run_test(target: str, port: int, timeout: float, headless: bool, retries: int, browser_channel: Optional[str] = "msedge", debug: bool = False) -> Dict[str, Any]:
    """Run tcp ping test via pingloc.com.

    Parameters mirror previous implementation; kept identical for compatibility.
    """
    url = "https://www.pingloc.com/tcp-ping"
    if target.startswith("http://") or target.startswith("https://"):
        import re as _re
        target = _re.sub(r"^https?://", "", target).rstrip('/')
    domain_port = f"{target}:{port}"
    start_time = time.time()
    attempt = 0
    last_error: Optional[str] = None
    while attempt <= retries:
        attempt += 1
        try:
            async with async_playwright() as p:
                launch_kwargs = {"headless": headless}
                if browser_channel:
                    launch_kwargs["channel"] = browser_channel
                try:
                    browser = await p.chromium.launch(**launch_kwargs)
                except Exception as be:
                    if browser_channel:
                        print(f"[WARN] Failed channel '{browser_channel}' ({be}); fallback to bundled.")
                        launch_kwargs.pop("channel", None)
                        browser = await p.chromium.launch(**launch_kwargs)
                    else:
                        raise
                context = await browser.new_context()
                page = await context.new_page()
                print(f"[INFO] Attempt {attempt}/{retries+1} navigating {url}")
                await page.goto(url, timeout=timeout * 1000)
                combo = page.locator('[role="combobox"]')
                await combo.fill(domain_port)
                await page.wait_for_timeout(500)
                try:
                    first_option = page.locator('[role="option"]').first
                    if await first_option.is_visible():
                        await first_option.click()
                except PlaywrightTimeoutError:
                    pass
                await page.locator('button:has-text("单次检测")').click(timeout=5000)
                try:
                    await page.wait_for_selector(PROGRESS_SELECTORS["progress_percent"], timeout=3000)
                except Exception:
                    pass
                try:
                    await page.wait_for_selector(TABLE_BODY_SELECTOR, timeout=3000)
                except Exception:
                    pass
                progress_locator = page.locator(PROGRESS_SELECTORS["progress_percent"])
                body = page.locator(TABLE_BODY_SELECTOR)
                poll_interval = 1.0
                deadline = time.time() + timeout
                percent_val = "0%"
                last_row_count = 0
                while time.time() < deadline:
                    done = False
                    if debug:
                        print(f"[DEBUG] Poll loop percent={percent_val} elapsed={round(time.time()-start_time,1)}s")
                    try:
                        txt = await progress_locator.inner_text(timeout=1500)
                        percent_val = txt.strip()
                        if percent_val.endswith('%'):
                            try:
                                num = float(percent_val.rstrip('%'))
                                if math.isfinite(num) and num >= 100:
                                    done = True
                            except ValueError:
                                pass
                    except Exception:
                        pass
                    try:
                        if await body.count() > 0:
                            rows_locator = body.locator('tr[ref]')
                            rc = await rows_locator.count()
                            if rc > 0 and rc == last_row_count and rc >= 5 and percent_val.startswith('100'):
                                done = True
                            last_row_count = rc
                            if rc > 0 and percent_val.startswith('100'):
                                done = True
                    except Exception:
                        pass
                    if done:
                        break
                    await page.wait_for_timeout(int(poll_interval * 1000))
                if not percent_val.startswith('100'):
                    print(f"[WARN] Progress end without 100% (last={percent_val})")
                elif debug:
                    print("[DEBUG] Progress reached 100%")
                async def get_text(sel: str):
                    try:
                        return (await page.locator(sel).inner_text(timeout=2000)).strip()
                    except Exception:
                        return None
                def num_or_none(v):
                    if not v:
                        return None
                    import re
                    m = re.search(r"(\d+(?:\.\d+)?)", v)
                    return float(m.group(1)) if m else None
                summary = {
                    "fastest": num_or_none(await get_text(PROGRESS_SELECTORS['fastest'])),
                    "slowest": num_or_none(await get_text(PROGRESS_SELECTORS['slowest'])),
                    "domestic_avg_ms": num_or_none(await get_text(PROGRESS_SELECTORS['domestic_avg'])),
                    "foreign_avg_ms": num_or_none(await get_text(PROGRESS_SELECTORS['foreign_avg'])),
                }
                if all(v is None for v in summary.values()):
                    try:
                        page_text = await page.content()
                        import re as _re
                        def grab(pattern: str):
                            m = _re.search(pattern, page_text)
                            if m:
                                try:
                                    return float(m.group(1))
                                except ValueError:
                                    return None
                            return None
                        summary['fastest'] = grab(r"最快[^0-9]*(\d+(?:\.\d+)?)ms") or summary['fastest']
                        summary['slowest'] = grab(r"最慢[^0-9]*(\d+(?:\.\d+)?)ms") or summary['slowest']
                        summary['domestic_avg_ms'] = grab(r"国内平均[^0-9]*(\d+(?:\.\d+)?)ms") or summary['domestic_avg_ms']
                        summary['foreign_avg_ms'] = grab(r"海外平均[^0-9]*(\d+(?:\.\d+)?)ms") or summary['foreign_avg_ms']
                        if any(v is not None for v in summary.values()):
                            print("[INFO] Summary metrics recovered via fallback pattern search")
                        else:
                            print("[WARN] Summary metrics not found via selectors or fallback patterns")
                    except Exception as se:
                        print(f"[DEBUG] Summary fallback failed: {se}")
                overview: List[OverviewEntry] = []
                for row_ref, provider_name, refs in OVERVIEW_ROWS:
                    if debug:
                        present = await page.locator(f'[ref={row_ref}]').count()
                        print(f"[DEBUG] Overview row ref={row_ref} present={present}")
                    if await page.locator(f'[ref={row_ref}]').count() == 0:
                        continue
                    fast_node = await get_text(f'[ref={refs[0]}]')
                    fast_ms = num_or_none(await get_text(f'[ref={refs[1]}]'))
                    slow_node = await get_text(f'[ref={refs[2]}]')
                    slow_ms = num_or_none(await get_text(f'[ref={refs[3]}]'))
                    avg_ms = num_or_none(await get_text(f'[ref={refs[4]}]'))
                    overview.append(OverviewEntry(provider=provider_name, fastest_node=fast_node, fastest_ms=fast_ms, slowest_node=slow_node, slowest_ms=slow_ms, average_ms=avg_ms))
                probes: List[ProbeRow] = []
                body = page.locator(TABLE_BODY_SELECTOR)
                if await body.count() > 0:
                    rows = body.locator('tr[ref]')
                    total = await rows.count()
                    if debug:
                        print(f"[DEBUG] Primary table body located; rows with ref: {total}")
                        sample_dump = []
                    for i in range(total):
                        tr = rows.nth(i)
                        tds = tr.locator('td')
                        c = await tds.count()
                        if c < 5:
                            continue
                        texts = []
                        for j in range(min(c, 5)):
                            try:
                                texts.append((await tds.nth(j).inner_text()).strip())
                            except Exception:
                                texts.append('')
                        if debug and len(sample_dump) < 8:
                            sample_dump.append(texts)
                        loc_cell, ip_cell, ip_loc_cell, latency_cell, sponsor_cell = texts
                        parts = loc_cell.split()
                        provider = parts[0] if parts else None
                        location = ' '.join(parts[1:]) if len(parts) > 1 else None
                        latency_ms, timeout_flag = _parse_latency(latency_cell)
                        sponsor = sponsor_cell if sponsor_cell != '--' else None
                        probes.append(ProbeRow(provider=provider, location=location, ip=ip_cell or None, ip_location=ip_loc_cell or None, latency_ms=latency_ms, timeout=timeout_flag, sponsor=sponsor))
                    if debug and total and not probes:
                        print("[DEBUG] Rows existed but no probes parsed -> possible column structure change")
                    if debug and 'sample_dump' in locals():
                        try:
                            dump_dir = Path('tcpping/debug')
                            dump_dir.mkdir(parents=True, exist_ok=True)
                            (dump_dir / 'rows_sample.json').write_text(json.dumps(sample_dump, ensure_ascii=False, indent=2), encoding='utf-8')
                            print("[DEBUG] Wrote row sample -> tcpping/debug/rows_sample.json")
                        except Exception as de:
                            print(f"[DEBUG] Failed writing rows_sample.json: {de}")
                elif debug:
                    print("[DEBUG] Primary table body selector not found; will attempt heuristic scan later if needed")
                if not probes and debug:
                    try:
                        dump_dir = Path('tcpping/debug')
                        dump_dir.mkdir(parents=True, exist_ok=True)
                        html_path = dump_dir / 'page.html'
                        with html_path.open('w', encoding='utf-8') as fhtml:
                            fhtml.write(await page.content())
                        shot_path = dump_dir / 'page.png'
                        await page.screenshot(path=str(shot_path), full_page=True)
                        print(f"[DEBUG] Dumped HTML -> {html_path}, screenshot -> {shot_path}")
                    except Exception as de:
                        print(f"[DEBUG] Failed diagnostic dump: {de}")
                if not probes:
                    try:
                        generic_rows = page.locator('tr')
                        gr_count = await generic_rows.count()
                        if debug:
                            print(f"[DEBUG] Heuristic scan over generic tr count={gr_count}")
                        extracted = 0
                        for i in range(min(gr_count, 300)):
                            tr = generic_rows.nth(i)
                            tds = tr.locator('td')
                            c = await tds.count()
                            if c < 4:
                                continue
                            texts = []
                            skip = True
                            for j in range(c):
                                try:
                                    t = (await tds.nth(j).inner_text()).strip()
                                except Exception:
                                    t = ''
                                texts.append(t)
                                if 'ms' in t or '超时' in t:
                                    skip = False
                            if skip:
                                continue
                            loc_cell = texts[0]
                            ip_cell = texts[1] if len(texts) > 1 else ''
                            ip_loc_cell = texts[2] if len(texts) > 2 else ''
                            latency_cell = ' '.join(texts)
                            sponsor_cell = texts[4] if len(texts) > 4 else ''
                            latency_ms, timeout_flag = _parse_latency(latency_cell)
                            if latency_ms is None and not timeout_flag:
                                continue
                            parts = loc_cell.split()
                            provider = parts[0] if parts else None
                            location = ' '.join(parts[1:]) if len(parts) > 1 else None
                            sponsor = sponsor_cell if sponsor_cell and sponsor_cell != '--' else None
                            probes.append(ProbeRow(provider=provider, location=location, ip=ip_cell or None, ip_location=ip_loc_cell or None, latency_ms=latency_ms, timeout=timeout_flag, sponsor=sponsor))
                            extracted += 1
                        if extracted:
                            print(f"[INFO] Fallback extracted {extracted} probe rows heuristically")
                        elif debug:
                            print("[DEBUG] Heuristic scan found no candidate rows with ms/超时 patterns")
                    except Exception as fe:
                        print(f"[DEBUG] Fallback row scan failed: {fe}")
                if not probes:
                    print("[WARN] No probe rows extracted (primary + fallback). Use debug=True for diagnostics.")
                result = {
                    "host": domain_port,
                    "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    "summary": summary,
                    "overview": [asdict(o) for o in overview],
                    "probes": [asdict(p) for p in probes],
                    "probe_count": len(probes),
                    "timeouts": sum(1 for p in probes if p.timeout),
                    "attempt": attempt,
                    "duration_sec": round(time.time() - start_time, 2),
                }
                await browser.close()
                return result
        except Exception as e:
            last_error = f"Attempt {attempt} failed: {e.__class__.__name__}: {e}"
            print(f"[ERROR] {last_error}")
            if attempt > retries:
                raise
            await asyncio.sleep(1.5)
    raise RuntimeError(last_error or "Unknown failure after retries")

mcp = FastMCP("tcpping-server")

@mcp.tool
async def tcpping_run(
    target: str,
    port: int = 443,
    timeout: float = 120,
    retries: int = 1,
    headless: bool = True,
    browser_channel: str = "msedge",
    debug: bool = False,
    summary_only: bool = False,
    auto_headed_retry: bool = True,
) -> str:
    """Run a distributed TCP latency test ("TCP ping") against a host:port via pingloc.com.

    This tool automates a real browser session (Playwright) to submit a single test
    request, then scrapes result tables and summary metrics (fastest, slowest, domestic / foreign averages).

    Parameters
    ----------
    target : str
        DNS name or IP (don't include scheme). Example: "admin.exchange.microsoft.com".
    port : int, default 443
        TCP port to test.
    timeout : float, default 120
        Overall timeout (seconds) for page load + polling the progress indicators.
    retries : int, default 1
        Additional retry attempts (headless) on failure before giving up.
    headless : bool, default True
        Run the browser headless. If results are empty and auto_headed_retry is True, a headed retry is attempted.
    browser_channel : str, default "msedge"
        Preferred Chromium channel (e.g. msedge, chrome, chromium). Falls back automatically if unavailable.
    debug : bool, default False
        Enable verbose logging and diagnostic artifact dumps (HTML / screenshot) when parsing fails.
    summary_only : bool, default False
        If True, return only high-level summary instead of full probe list.
    auto_headed_retry : bool, default True
        Perform one additional headed (non-headless) run when headless produced no probes & no summary metrics.

    Returns
    -------
    str (JSON)
        JSON string containing either the full dataset or summary-only view. Keys include:
        host, generated_at, summary{fastest, slowest, domestic_avg_ms, foreign_avg_ms},
        overview[], probes[], probe_count, timeouts, duration_sec, headed_retry (bool when attempted).

    Notes
    -----
    - This is a best-effort scrape of a third-party site; layout changes can break parsing.
    - Use debug=True to capture page artifacts under tcpping/debug/ for troubleshooting.
    """
    data = await run_test(target=target, port=port, timeout=timeout, headless=headless, retries=retries, browser_channel=browser_channel, debug=debug)
    if auto_headed_retry and headless and data.get("probe_count", 0) == 0 and all(v is None for v in data.get("summary", {}).values()):
        # Retry once in headed mode to work around sites that block / lazy-render in headless
        try:
            print("[INFO] Empty result in headless mode; retrying headed (visible browser)...")
            headed = await run_test(target=target, port=port, timeout=timeout, headless=False, retries=0, browser_channel=browser_channel, debug=debug)
            # Prefer headed result if it has probes or summary values
            if headed.get("probe_count", 0) > 0 or any(v is not None for v in headed.get("summary", {}).values()):
                headed["headed_retry"] = True
                data = headed
            else:
                data["headed_retry"] = False
        except Exception as re:
            print(f"[WARN] Headed retry failed: {re}")
    if summary_only:
        minimal = {
            "host": data.get("host"),
            "generated_at": data.get("generated_at"),
            "summary": data.get("summary"),
            "probe_count": data.get("probe_count"),
            "timeouts": data.get("timeouts"),
            "duration_sec": data.get("duration_sec"),
            "headed_retry": data.get("headed_retry", False),
        }
        return json.dumps(minimal, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)

VERSION = "0.1.5"

@mcp.resource("tcpping://info")
def get_server_info() -> dict:
    return {
        "name": "TCP Ping MCP Server",
        "version": VERSION,
        "description": "Provides TCP connectivity testing via pingloc.com",
        "supported_channels": ["msedge", "chrome", "chromium"],
        "default_port": 443,
        "default_timeout": 120,
    }

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()
