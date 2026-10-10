import asyncio
import time
import httpx
from rich.console import Console
from rich.table import Table

# Параметри фільтрації
MIN_VOLUME_USDT = 80_000
MAX_VOLUME_USDT = 5_000_000
MIN_SPREAD_PCT = 0.35
MAX_SPREAD_PCT = 2.00
MIN_EDGE_HITS_PCT = 35.0  # Мінімум 35% угод мають бити по реальних краях стакану!

TICKER_URL = "https://api.mexc.com/api/v3/ticker/24hr"
API_SYMBOLS_URL = "https://api.mexc.com/api/v3/defaultSymbols"
TRADES_URL = "https://api.mexc.com/api/v3/trades"
DEPTH_URL = "https://api.mexc.com/api/v3/depth"


async def analyze_pair_quality(client: httpx.AsyncClient, candidate: dict, sem: asyncio.Semaphore):
    """Глибокий рентген пари: перевіряє пульс угод та відсіює Wash-ботів."""
    symbol = candidate["symbol"]
    async with sem:
        try:
            depth_resp, trades_resp = await asyncio.gather(
                client.get(DEPTH_URL, params={"symbol": symbol, "limit": 5}),
                client.get(TRADES_URL, params={"symbol": symbol, "limit": 20})
            )
            if depth_resp.status_code != 200 or trades_resp.status_code != 200:
                return None

            depth = depth_resp.json()
            trades = trades_resp.json()
            if not trades or not depth.get("bids") or not depth.get("asks"):
                return None

            best_bid = float(depth["bids"][0][0])
            best_ask = float(depth["asks"][0][0])

            # Перевіряємо, щоб між Bid та Ask було хоча б кілька тіків (відсікаємо MIUUSDT)
            if len(depth["bids"]) > 1:
                tick_approx = abs(best_bid - float(depth["bids"][1][0]))
                if tick_approx > 0 and (best_ask - best_bid) / tick_approx < 3:
                    return None

            now_ms = int(time.time() * 1000)
            latest_ms = max(t["time"] for t in trades)
            last_sec_ago = max(0.0, (now_ms - latest_ms) / 1000.0)

            # Відсікаємо, якщо остання угода була більше 3 хвилин тому
            if last_sec_ago > 180:
                return None

            # Рахуємо, скільки угод реально вдарили по Bid або Ask, а не всередині спреду
            edge_hits = 0
            bid_hits = 0
            ask_hits = 0
            for t in trades:
                p = float(t["price"])
                if p <= best_bid:
                    edge_hits += 1
                    bid_hits += 1
                elif p >= best_ask:
                    edge_hits += 1
                    ask_hits += 1

            edge_hit_pct = (edge_hits / len(trades)) * 100

            # Нам потрібні пари, де реально б'ють і по Bid (купують у нас), і по Ask (продають нам)
            if edge_hit_pct >= MIN_EDGE_HITS_PCT:
                candidate["best_bid"] = best_bid
                candidate["best_ask"] = best_ask
                candidate["spread_pct"] = ((best_ask - best_bid) / best_bid) * 100
                candidate["edge_hit_pct"] = edge_hit_pct
                candidate["bid_ask_hits"] = f"{bid_hits}B / {ask_hits}A"
                candidate["last_sec"] = last_sec_ago
                return candidate
        except Exception:
            return None
    return None


async def run_pro_scanner():
    console = Console()
    console.print("[bold cyan]1. Отримуємо всі API-пари з MEXC...[/bold cyan]")

    async with httpx.AsyncClient(timeout=10.0) as client:
        sym_resp, tick_resp = await asyncio.gather(
            client.get(API_SYMBOLS_URL),
            client.get(TICKER_URL)
        )
        api_allowed = set(sym_resp.json().get("data", []))
        tickers = tick_resp.json()

        pre_list = []
        for item in tickers:
            sym = item.get("symbol", "")
            # Відсікаємо токенізовані акції (...ONUSDT) та токени з плечем
            if sym not in api_allowed or not sym.endswith("USDT"):
                continue
            if any(x in sym for x in ("3L", "3S", "ONUSDT")):
                continue

            try:
                bid = float(item.get("bidPrice") or 0)
                ask = float(item.get("askPrice") or 0)
                vol = float(item.get("quoteVolume") or 0)
            except ValueError:
                continue

            if bid <= 0 or ask <= bid:
                continue

            spread = ((ask - bid) / bid) * 100
            if (MIN_VOLUME_USDT <= vol <= MAX_VOLUME_USDT) and (MIN_SPREAD_PCT <= spread <= MAX_SPREAD_PCT):
                pre_list.append({
                    "symbol": sym,
                    "spread_pct": spread,
                    "vol": vol,
                })

        console.print(
            f"[bold cyan]2. Знайдено {len(pre_list)} кандидатів. Запускаємо рентген проти Wash-ботів...[/bold cyan]")

        # Обмежуємо паралельні запити до 10, щоб не зловити Rate Limit
        sem = asyncio.Semaphore(10)
        tasks = [analyze_pair_quality(client, c, sem) for c in pre_list[:60]]
        results = await asyncio.gather(*tasks)

        clean_pairs = [r for r in results if r is not None]
        # Сортуємо за відсотком реальних ударів у стакан
        clean_pairs.sort(key=lambda x: (x["edge_hit_pct"], x["spread_pct"]), reverse=True)

    table = Table(title=f"Чисті стакани без Wash-ботів ({len(clean_pairs)} пар пройшли перевірку)")
    table.add_column("Пара", style="bold yellow")
    table.add_column("Bid ($)", justify="right", style="green")
    table.add_column("Ask ($)", justify="right", style="red")
    table.add_column("Спред %", justify="right", style="bold magenta")
    table.add_column("Реальні удари в стакан %", justify="right", style="bold green")
    table.add_column("Удари (Bid/Ask)", justify="center", style="cyan")
    table.add_column("Остання угода", justify="right")

    for c in clean_pairs[:20]:
        table.add_row(
            c["symbol"],
            f"{c['best_bid']:.6g}",
            f"{c['best_ask']:.6g}",
            f"{c['spread_pct']:.2f}%",
            f"{c['edge_hit_pct']:.0f}%",
            c["bid_ask_hits"],
            f"{c['last_sec']:.0f}с тому"
        )

    console.print(table)


if __name__ == "__main__":
    asyncio.run(run_pro_scanner())