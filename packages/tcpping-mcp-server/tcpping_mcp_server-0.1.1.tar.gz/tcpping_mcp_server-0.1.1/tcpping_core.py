"""Self-contained core logic for tcp ping scraping used by FastMCP server.

Extracted from run_tcpping.py to avoid external dependency when packaging only
this directory.
"""
from __future__ import annotations

import asyncio
import math
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

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

def _parse_latency(text: str) -> tuple[Optional[float], bool]:
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
                    print(f"[INFO] Using browser channel: {browser_channel}")
                try:
                    browser = await p.chromium.launch(**launch_kwargs)
                except Exception as be:
                    if browser_channel:
                        print(f"[WARN] Failed to launch channel '{browser_channel}' ({be}); falling back to bundled Chromium.")
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

                progress_locator = page.locator(PROGRESS_SELECTORS["progress_percent"])
                body = page.locator(TABLE_BODY_SELECTOR)
                poll_interval = 1.0
                deadline = time.time() + timeout
                percent_val = "0%"
                last_row_count = 0
                while time.time() < deadline:
                    done = False
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
                    print(f"[WARN] Progress loop end without confirmed 100% (last={percent_val})")

                async def get_text(sel: str) -> Optional[str]:
                    try:
                        return (await page.locator(sel).inner_text(timeout=2000)).strip()
                    except Exception:
                        return None

                fastest_t = await get_text(PROGRESS_SELECTORS['fastest'])
                slowest_t = await get_text(PROGRESS_SELECTORS['slowest'])
                domestic_t = await get_text(PROGRESS_SELECTORS['domestic_avg'])
                foreign_t = await get_text(PROGRESS_SELECTORS['foreign_avg'])

                def num_or_none(v: Optional[str]) -> Optional[float]:
                    if not v:
                        return None
                    import re
                    m = re.search(r"(\d+(?:\.\d+)?)", v)
                    return float(m.group(1)) if m else None

                summary = {
                    "fastest": num_or_none(fastest_t),
                    "slowest": num_or_none(slowest_t),
                    "domestic_avg_ms": num_or_none(domestic_t),
                    "foreign_avg_ms": num_or_none(foreign_t),
                }

                if all(v is None for v in summary.values()):
                    try:
                        page_text = (await page.content())
                        import re as _re
                        def grab(pattern: str) -> Optional[float]:
                            m = _re.search(pattern, page_text)
                            if m:
                                try:
                                    return float(m.group(1))
                                except ValueError:
                                    return None
                            return None
                        summary['fastest'] = summary['fastest'] or grab(r"最快[^0-9]*(\d+(?:\.\d+)?)ms")
                        summary['slowest'] = summary['slowest'] or grab(r"最慢[^0-9]*(\d+(?:\.\d+)?)ms")
                        summary['domestic_avg_ms'] = summary['domestic_avg_ms'] or grab(r"国内平均[^0-9]*(\d+(?:\.\d+)?)ms")
                        summary['foreign_avg_ms'] = summary['foreign_avg_ms'] or grab(r"海外平均[^0-9]*(\d+(?:\.\d+)?)ms")
                        if all(v is None for v in summary.values()):
                            print("[WARN] Summary metrics not found via selectors or fallback patterns")
                        else:
                            print("[INFO] Summary metrics recovered via fallback pattern search")
                    except Exception as se:
                        print(f"[DEBUG] Summary fallback failed: {se}")

                overview: List[OverviewEntry] = []
                for row_ref, provider_name, refs in OVERVIEW_ROWS:
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
                    for i in range(total):
                        tr = rows.nth(i)
                        tds = tr.locator('td')
                        c = await tds.count()
                        if c < 5:
                            continue
                        texts = []
                        for j in range(min(c, 5)):
                            try:
                                cell_text = (await tds.nth(j).inner_text()).strip()
                            except Exception:
                                cell_text = ''
                            texts.append(cell_text)
                        if len(texts) < 5:
                            continue
                        loc_cell, ip_cell, ip_loc_cell, latency_cell, sponsor_cell = texts
                        parts = loc_cell.split()
                        provider = parts[0] if parts else None
                        location = ' '.join(parts[1:]) if len(parts) > 1 else None
                        latency_ms, timeout_flag = _parse_latency(latency_cell)
                        sponsor = sponsor_cell if sponsor_cell != '--' else None
                        probes.append(ProbeRow(provider=provider, location=location, ip=ip_cell or None, ip_location=ip_loc_cell or None, latency_ms=latency_ms, timeout=timeout_flag, sponsor=sponsor))
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
                    except Exception as fe:
                        print(f"[DEBUG] Fallback row scan failed: {fe}")

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
                if not probes:
                    print("[WARN] No probe rows extracted (primary + fallback). Use debug for diagnostics.")
                await browser.close()
                return result
        except Exception as e:
            last_error = f"Attempt {attempt} failed: {e.__class__.__name__}: {e}"
            print(f"[ERROR] {last_error}")
            if attempt > retries:
                raise
            await asyncio.sleep(1.5)
    raise RuntimeError(last_error or "Unknown failure after retries")
