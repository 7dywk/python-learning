import asyncio
import json
import time
import httpx
import websockets
from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Беремо монету з широким двостороннім спредом із нашого сканера!
SYMBOL = "FONEUSDT"          # Спробуй також EMBERUSDT, ZCUSDT, FLORKUSDT
MIN_PROFIT_SPREAD = 0.35     # Мінімальний чистий спред (%) для входу
ORDER_SIZE_USD = 15.0        # Наш тестовий ордер ($15)

state = {
    "tick_size": 0.000001,
    "decimals": 6,
    "mexc_bids": [],
    "mexc_asks": [],
    "mexc_spread_pct": 0.0,
    "free_ticks": 0,
    "btc_price": 0.0,
    "btc_10s_change": 0.0,
    "target_buy": 0.0,
    "target_sell": 0.0,
    "net_profit_pct": 0.0,
    "net_profit_usd": 0.0,
    "status": "Ініціалізація...",
    "status_style": "yellow"
}

btc_history = []  # Зберігаємо ціну BTC за останні 10 секунд для детектора паніки

async def fetch_symbol_rules():
    """Автоматично дістає точний крок ціни (tick_size) з біржі MEXC."""
    url = "https://api.mexc.com/api/v3/exchangeInfo"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"symbol": SYMBOL})
        if resp.status_code == 200:
            data = resp.json()
            symbols = data.get("symbols", [])
            if symbols:
                prec = int(symbols[0].get("quoteAssetPrecision", 6))
                state["decimals"] = prec
                state["tick_size"] = 10 ** (-prec)

def calculate_bot_logic():
    if not state["mexc_bids"] or not state["mexc_asks"]:
        return

    best_bid = state["mexc_bids"][0][0]
    best_ask = state["mexc_asks"][0][0]
    tick = state["tick_size"]
    prec = state["decimals"]

    # Скільки мінімальних кроків ціни (тіків) зараз всередині спреду
    if len(state["mexc_bids"]) > 1:
        # Оцінюємо реальний крок між рівнями стакану
        real_step = round(abs(state["mexc_bids"][0][0] - state["mexc_bids"][1][0]), prec)
        if real_step > 0 and real_step < tick:
            tick = real_step

    free_ticks = int(round((best_ask - best_bid) / tick)) - 1
    state["free_ticks"] = max(0, free_ticks)
    state["mexc_spread_pct"] = ((best_ask - best_bid) / best_bid) * 100

    # 1. Перевірка паніки по BTC (якщо біткоїн впав > 0.15% за 10 секунд)
    if state["btc_10s_change"] <= -0.15:
        state["status"] = f"🚨 PANIC CANCEL! BTC різко летить вниз ({state['btc_10s_change']:.2f}% за 10с). Знімаємо лімітки!"
        state["status_style"] = "bold white on red"
        return

    # 2. Перевірка, чи є куди фізично ставити лімітки (+1 тік і -1 тік)
    if state["free_ticks"] < 2:
        state["status"] = f"⏸ Стінка впритул (вільних тіків: {state['free_ticks']}). Немає простору для +1 тік."
        state["status_style"] = "yellow"
        return

    target_buy = round(best_bid + tick, prec)
    target_sell = round(best_ask - tick, prec)
    net_pct = ((target_sell - target_buy) / target_buy) * 100
    net_usd = ORDER_SIZE_USD * (net_pct / 100.0)

    state["target_buy"] = target_buy
    state["target_sell"] = target_sell
    state["net_profit_pct"] = net_pct
    state["net_profit_usd"] = net_usd

    if net_pct < MIN_PROFIT_SPREAD:
        state["status"] = f"⏸ Мала рентабельність: якщо станемо вперед, залишиться {net_pct:.2f}% (< {MIN_PROFIT_SPREAD}%)"
        state["status_style"] = "yellow"
    else:
        state["status"] = (
            f"✅ БОЙОВИЙ РЕЖИМ: Купівля {target_buy:.{prec}f} (+1 тік) ➔ Продаж {target_sell:.{prec}f} (-1 тік) | "
            f"Чистий профіт: +{net_pct:.2f}% (+${net_usd:.3f} з ордера ${ORDER_SIZE_USD:.0f})"
        )
        state["status_style"] = "bold green"

async def mexc_depth_stream():
    url = "https://api.mexc.com/api/v3/depth"
    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            try:
                resp = await client.get(url, params={"symbol": SYMBOL, "limit": 5})
                if resp.status_code == 200:
                    data = resp.json()
                    state["mexc_bids"] = [[float(p), float(q)] for p, q in data.get("bids", [])]
                    state["mexc_asks"] = [[float(p), float(q)] for p, q in data.get("asks", [])]
                    calculate_bot_logic()
            except Exception:
                pass
            await asyncio.sleep(0.25)

async def binance_btc_guard():
    """Слухає BTCUSDT на Binance як глобальний індикатор небезпеки проливу."""
    ws_url = "wss://stream.binance.com:9443/ws/btcusdt@bookTicker"
    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                async for msg in ws:
                    data = json.loads(msg)
                    price = float(data["b"])
                    now = time.time()
                    state["btc_price"] = price
                    btc_history.append((now, price))
                    # Залишаємо тільки останні 10 секунд
                    while btc_history and now - btc_history[0][0] > 10.0:
                        btc_history.pop(0)
                    if btc_history:
                        old_price = btc_history[0][1]
                        state["btc_10s_change"] = ((price - old_price) / old_price) * 100
        except Exception:
            await asyncio.sleep(2)

def render_dashboard() -> Panel:
    prec = state["decimals"]
    info_text = Text.from_markup(
        f"Спред у стакані: [bold magenta]{state['mexc_spread_pct']:.2f}%[/bold magenta] "
        f"(Вільних кроків всередині: [bold cyan]{state['free_ticks']}[/bold cyan])   |   "
        f"Радар BTC: [bold yellow]${state['btc_price']:,.1f}[/bold yellow] ({state['btc_10s_change']:+.2f}% / 10с)\n"
        f"[{state['status_style']}]{state['status']}[/{state['status_style']}]"
    )

    table = Table(expand=True)
    table.add_column("Рівень", justify="center", style="dim")
    table.add_column("MEXC Bid ($ обсяг)", justify="right", style="green")
    table.add_column("MEXC Ціна Bid", justify="right", style="bold green")
    table.add_column("MEXC Ціна Ask", justify="left", style="bold red")
    table.add_column("MEXC Ask ($ обсяг)", justify="left", style="red")

    for i in range(5):
        b_p, b_q = state["mexc_bids"][i] if i < len(state["mexc_bids"]) else (0.0, 0.0)
        a_p, a_q = state["mexc_asks"][i] if i < len(state["mexc_asks"]) else (0.0, 0.0)
        table.add_row(
            f"#{i+1}",
            f"${b_p * b_q:,.1f}" if b_p else "-",
            f"{b_p:.{prec}f}" if b_p else "-",
            f"{a_p:.{prec}f}" if a_p else "-",
            f"${a_p * a_q:,.1f}" if a_p else "-",
            style="bold" if i == 0 else None
        )

    return Panel(Group(info_text, table), title=f"Термінал Скальпера [{SYMBOL}]", border_style="cyan")

async def main():
    console = Console()
    await fetch_symbol_rules()
    tasks = [
        asyncio.create_task(mexc_depth_stream()),
        asyncio.create_task(binance_btc_guard())
    ]
    with Live(render_dashboard(), refresh_per_second=8, console=console) as live:
        try:
            while True:
                live.update(render_dashboard())
                await asyncio.sleep(0.12)
        except KeyboardInterrupt:
            for t in tasks:
                t.cancel()

if __name__ == "__main__":
    asyncio.run(main())