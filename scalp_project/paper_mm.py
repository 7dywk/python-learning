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

SYMBOL = "FONEUSDT"            # Монета для торгівлі
ORDER_SIZE_USD = 20.0          # Оптимальний розмір ордера ($20)
DUST_THRESHOLD_USD = 8.0       # Ігноруємо пилюку < $8 при ПОКУПЦІ
MIN_PROFIT_SPREAD = 0.35       # Мінімальний спред для входу (%)
MAX_TAKE_PROFIT_PCT = 0.85     # Не жадібнічаємо: макс. ціль тейка (+0.85% для швидкого обігу)
MIN_REPEG_INTERVAL = 2.5       # Мінімум 2.5 сек між перестановками ордера (Анти-спам API)
MIN_REPEG_TICKS = 3            # Не смикаємо ордер через зсув на 1-2 тіки

state = {
    "tick_size": 0.000001,
    "decimals": 6,
    "mexc_bids": [],
    "mexc_asks": [],
    "btc_price": 0.0,
    "btc_10s_change": 0.0,
    "bot_mode": "LOOKING_TO_BUY",
    "my_buy_price": 0.0,
    "my_sell_price": 0.0,
    "entry_price": 0.0,
    "last_repeg_time": 0.0,
    "total_pnl_usd": 0.0,
    "unrealized_pnl_usd": 0.0,
    "completed_cycles": 0,
    "repeg_count": 0,
    "market_trades_seen": 0,
    "status": "Запуск симулятора...",
    "status_style": "yellow",
    "trade_logs": [],
    "market_tape": []
}

btc_history = []
last_seen_trade_ms = int(time.time() * 1000)

def log_bot_event(msg: str):
    t_str = time.strftime("%H:%M:%S")
    state["trade_logs"].insert(0, f"[{t_str}] {msg}")
    if len(state["trade_logs"]) > 6:
        state["trade_logs"].pop()

def log_market_tape(msg: str):
    t_str = time.strftime("%H:%M:%S")
    state["market_tape"].insert(0, f"[{t_str}] {msg}")
    if len(state["market_tape"]) > 6:
        state["market_tape"].pop()

async def fetch_symbol_rules():
    url = "https://api.mexc.com/api/v3/exchangeInfo"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params={"symbol": SYMBOL})
        if resp.status_code == 200:
            symbols = resp.json().get("symbols", [])
            if symbols:
                prec = int(symbols[0].get("quoteAssetPrecision", 6))
                state["decimals"] = prec
                state["tick_size"] = 10 ** (-prec)

def pick_smart_wall(levels: list, threshold_usd: float) -> tuple[float, int]:
    """Шукає першу стінку >= threshold_usd."""
    if not levels:
        return 0.0, 0
    for idx, (price, qty) in enumerate(levels):
        if price * qty >= threshold_usd:
            return price, idx + 1
    return levels[0][0], 1

def can_repeg(current_order_price: float, new_target_price: float) -> bool:
    """Перевіряє, чи варто переставляти ордер (захист від спаму запитами)."""
    if current_order_price == 0.0:
        return True
    now = time.time()
    if now - state["last_repeg_time"] < MIN_REPEG_INTERVAL:
        return False
    diff_ticks = abs(new_target_price - current_order_price) / state["tick_size"]
    return diff_ticks >= MIN_REPEG_TICKS

def update_bot_orders():
    if not state["mexc_bids"] or not state["mexc_asks"]:
        return

    tick = state["tick_size"]
    prec = state["decimals"]
    best_bid = state["mexc_bids"][0][0]
    best_ask = state["mexc_asks"][0][0]

    # Купуємо тільки перед надійною плитою (>= $8)
    ref_bid, bid_lvl = pick_smart_wall(state["mexc_bids"], DUST_THRESHOLD_USD)
    # Для оцінки спреду дивимось на стінку продавців
    ref_ask, ask_lvl = pick_smart_wall(state["mexc_asks"], DUST_THRESHOLD_USD)

    target_buy = round(ref_bid + tick, prec)
    if target_buy >= best_ask:
        target_buy = best_bid

    # РЕЖИМ 1: Шукаємо покупку (LOOKING_TO_BUY)
    if state["bot_mode"] == "LOOKING_TO_BUY":
        state["unrealized_pnl_usd"] = 0.0
        if state["btc_10s_change"] <= -0.15:
            if state["my_buy_price"] != 0.0:
                log_bot_event(f"🚨 PANIC: Зняли BUY через падіння BTC ({state['btc_10s_change']:.2f}%)")
            state["my_buy_price"] = 0.0
            state["status"] = f"🚨 PANIC: BTC падає ({state['btc_10s_change']:.2f}%). Поза ринком!"
            state["status_style"] = "bold white on red"
            return

        pot_sell = round(ref_ask - tick, prec)
        pot_spread = ((pot_sell - target_buy) / target_buy) * 100

        if pot_spread < MIN_PROFIT_SPREAD:
            state["my_buy_price"] = 0.0
            state["status"] = f"⏸ Спред вузький ({pot_spread:.2f}%). Чекаємо розширення..."
            state["status_style"] = "yellow"
        else:
            if can_repeg(state["my_buy_price"], target_buy):
                old_p = state["my_buy_price"]
                state["my_buy_price"] = target_buy
                state["last_repeg_time"] = time.time()
                state["repeg_count"] += 1
                if old_p == 0.0:
                    log_bot_event(f"📌 Поставили BUY по {target_buy:.{prec}f} (перед #{bid_lvl})")
                else:
                    log_bot_event(f"🔄 Переставили BUY: {old_p:.{prec}f} ➔ {target_buy:.{prec}f} (перед #{bid_lvl})")

            state["status"] = (
                f"🟢 СТОЇТЬ BUY ПО: {state['my_buy_price']:.{prec}f} (перед #{bid_lvl}) | "
                f"Очікуваний спред: +{pot_spread:.2f}%"
            )
            state["status_style"] = "bold green"

    # РЕЖИМ 2: Монета куплена, виставляємо ШВИДКИЙ ТЕЙК (HOLDING_INVENTORY)
    elif state["bot_mode"] == "HOLDING_INVENTORY":
        # Рахуємо поточний плаваючий PnL, якби злили прямо зараз у Best Bid
        cur_pct = ((best_bid - state["entry_price"]) / state["entry_price"]) * 100
        state["unrealized_pnl_usd"] = ORDER_SIZE_USD * (cur_pct / 100.0)

        # Мінімальна ціна, де ми вже в хорошому плюсі (+0.35%)
        min_profitable_sell = round(state["entry_price"] * (1 + MIN_PROFIT_SPREAD / 100.0), prec)
        # Максимальна ціна (Анти-жадібність +0.85%), щоб не чекати +2.5% годинами!
        max_cap_sell = round(state["entry_price"] * (1 + MAX_TAKE_PROFIT_PCT / 100.0), prec)

        # Стаємо прямо перед першим же Ask #1 (щоб забрати першого ж покупця!),
        # але не нижче нашого мінімального плюса і не вище стелі жадібності
        front_ask_sell = round(best_ask - tick, prec)
        smart_sell = max(min_profitable_sell, min(front_ask_sell, max_cap_sell))

        if can_repeg(state["my_sell_price"], smart_sell):
            old_s = state["my_sell_price"]
            state["my_sell_price"] = smart_sell
            state["last_repeg_time"] = time.time()
            state["repeg_count"] += 1
            log_bot_event(f"🔄 Тейк SELL: {old_s:.{prec}f} ➔ {smart_sell:.{prec}f} (Швидкий вихід)")

        target_profit_pct = ((state["my_sell_price"] - state["entry_price"]) / state["entry_price"]) * 100
        state["status"] = (
            f"🟠 НА РУКАХ (Вхід: {state['entry_price']:.{prec}f}) ➔ "
            f"СТОЇТЬ SELL ПО: {state['my_sell_price']:.{prec}f} (+{target_profit_pct:.2f}%)"
        )
        state["status_style"] = "bold cyan"

async def mexc_market_loop():
    global last_seen_trade_ms
    depth_url = "https://api.mexc.com/api/v3/depth"
    trades_url = "https://api.mexc.com/api/v3/trades"

    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            try:
                d_resp, t_resp = await asyncio.gather(
                    client.get(depth_url, params={"symbol": SYMBOL, "limit": 6}),
                    client.get(trades_url, params={"symbol": SYMBOL, "limit": 15})
                )
                prec = state["decimals"]

                if d_resp.status_code == 200:
                    d_data = d_resp.json()
                    state["mexc_bids"] = [[float(p), float(q)] for p, q in d_data.get("bids", [])]
                    state["mexc_asks"] = [[float(p), float(q)] for p, q in d_data.get("asks", [])]
                    update_bot_orders()

                if t_resp.status_code == 200:
                    trades = t_resp.json()
                    trades.sort(key=lambda x: x["time"])
                    for t in trades:
                        if t["time"] <= last_seen_trade_ms:
                            continue
                        last_seen_trade_ms = t["time"]
                        state["market_trades_seen"] += 1

                        t_price = float(t["price"])
                        t_usd = t_price * float(t["qty"])
                        is_sell = t.get("isBuyerMaker", False)
                        side_str = "[red]SELL[/red]" if is_sell else "[green]BUY [/green]"

                        if state["bot_mode"] == "LOOKING_TO_BUY" and state["my_buy_price"] > 0:
                            if t_price <= state["my_buy_price"]:
                                state["entry_price"] = state["my_buy_price"]
                                state["bot_mode"] = "HOLDING_INVENTORY"
                                state["my_sell_price"] = 0.0  # Скидаємо, щоб миттєво виставити SELL
                                state["last_repeg_time"] = 0.0
                                log_market_tape(f"{side_str} по {t_price:.{prec}f} (${t_usd:.1f}) ➔ [bold green]🎯 ВЛУЧИЛИ В НАШ BUY![/bold green]")
                                log_bot_event(f"✅ КУПИЛИ по {state['entry_price']:.{prec}f} (Угода: ${t_usd:.1f})")
                                update_bot_orders()
                            else:
                                diff_ticks = int(round((t_price - state["my_buy_price"]) / state["tick_size"]))
                                log_market_tape(f"{side_str} по {t_price:.{prec}f} (${t_usd:.1f}) | До нашого BUY: {diff_ticks} тіків")

                        elif state["bot_mode"] == "HOLDING_INVENTORY" and state["my_sell_price"] > 0:
                            if t_price >= state["my_sell_price"]:
                                exit_p = state["my_sell_price"]
                                profit_pct = ((exit_p - state["entry_price"]) / state["entry_price"]) * 100
                                profit_usd = ORDER_SIZE_USD * (profit_pct / 100.0)
                                state["total_pnl_usd"] += profit_usd
                                state["completed_cycles"] += 1
                                state["bot_mode"] = "LOOKING_TO_BUY"
                                state["my_buy_price"] = 0.0
                                state["last_repeg_time"] = 0.0
                                log_market_tape(f"{side_str} по {t_price:.{prec}f} (${t_usd:.1f}) ➔ [bold cyan]💰 ЗАБРАЛИ НАШ ТЕЙК![/bold cyan]")
                                log_bot_event(f"💰 ПРОДАЛИ по {exit_p:.{prec}f}! Профіт: +{profit_pct:.2f}% (+${profit_usd:.3f})")
                                update_bot_orders()
                            else:
                                diff_ticks = int(round((state["my_sell_price"] - t_price) / state["tick_size"]))
                                log_market_tape(f"{side_str} по {t_price:.{prec}f} (${t_usd:.1f}) | До нашого SELL: {diff_ticks} тіків")
            except Exception:
                pass
            await asyncio.sleep(0.35)

async def binance_btc_guard():
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
                    while btc_history and now - btc_history[0][0] > 10.0:
                        btc_history.pop(0)
                    if btc_history:
                        old_p = btc_history[0][1]
                        state["btc_10s_change"] = ((price - old_p) / old_p) * 100
        except Exception:
            await asyncio.sleep(2)

def render_ui() -> Panel:
    prec = state["decimals"]
    unr_color = "green" if state["unrealized_pnl_usd"] >= 0 else "red"
    header = Text.from_markup(
        f"Зафіксовано PnL: [bold green]+${state['total_pnl_usd']:.3f}[/bold green] (Кіл: [bold yellow]{state['completed_cycles']}[/bold yellow]) | "
        f"В угоді зараз: [{unr_color}]{state['unrealized_pnl_usd']:+.3f}$[/{unr_color}] | "
        f"Переставлень: [bold cyan]{state['repeg_count']}[/bold cyan] | "
        f"Угод: [bold magenta]{state['market_trades_seen']}[/bold magenta]\n"
        f"[{state['status_style']}]{state['status']}[/{state['status_style']}]"
    )

    table = Table(expand=True)
    table.add_column("Рівень", justify="center", style="dim")
    table.add_column("MEXC Bid ($)", justify="right", style="green")
    table.add_column("Ціна Bid", justify="right", style="bold green")
    table.add_column("Ціна Ask", justify="left", style="bold red")
    table.add_column("MEXC Ask ($)", justify="left", style="red")

    for i in range(5):
        b_p, b_q = state["mexc_bids"][i] if i < len(state["mexc_bids"]) else (0.0, 0.0)
        a_p, a_q = state["mexc_asks"][i] if i < len(state["mexc_asks"]) else (0.0, 0.0)
        table.add_row(
            f"#{i+1}",
            f"${b_p * b_q:,.1f}" if b_p else "-",
            f"{b_p:.{prec}f}" if b_p else "-",
            f"{a_p:.{prec}f}" if a_p else "-",
            f"${a_p * a_q:,.1f}" if a_p else "-"
        )

    tape_str = "\n".join(state["market_tape"]) if state["market_tape"] else "Слухаємо стрічку угод біржі..."
    tape_panel = Panel(tape_str, title="📡 Жива стрічка угод на біржі", border_style="magenta")

    logs_str = "\n".join(state["trade_logs"]) if state["trade_logs"] else "Очікуємо дій бота..."
    logs_panel = Panel(logs_str, title="🤖 Дії нашого бота (З Анти-Спамом та Швидким Тейком)", border_style="yellow")

    return Panel(Group(header, table, tape_panel, logs_panel), title=f"Симулятор Маркетмейкера [{SYMBOL}] (Ордер ${ORDER_SIZE_USD:.0f})", border_style="cyan")

async def main():
    console = Console()
    await fetch_symbol_rules()
    log_bot_event(f"Старт PRO-симуляції на {SYMBOL} (Макс. тейк: +{MAX_TAKE_PROFIT_PCT}%, Анти-спам: {MIN_REPEG_TICKS} тіки)")
    tasks = [
        asyncio.create_task(mexc_market_loop()),
        asyncio.create_task(binance_btc_guard())
    ]
    with Live(render_ui(), refresh_per_second=6, console=console) as live:
        try:
            while True:
                live.update(render_ui())
                await asyncio.sleep(0.15)
        except KeyboardInterrupt:
            for t in tasks:
                t.cancel()

if __name__ == "__main__":
    asyncio.run(main())

