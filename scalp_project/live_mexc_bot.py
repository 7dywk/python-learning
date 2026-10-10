import asyncio
import hashlib
import hmac
import json
import math
import os
import time
from urllib.parse import urlencode

import httpx
import websockets
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# ================= НАЛАШТУВАННЯ БОЙОВОГО БОТА =================
API_KEY = os.getenv("MEXC_API_KEY", "mx0vgl9L2kKo5v7hqW")
SECRET_KEY = os.getenv("MEXC_SECRET_KEY", "4502a4b2553244928c6170f46ae45624")

SYMBOL = "FONEUSDT"
BASE_ASSET = SYMBOL.replace("USDT", "")
ORDER_SIZE_USD = 6.2
MIN_NOTIONAL_USD = 5.1

DUST_THRESHOLD_USD = 15.0
MIN_PROFIT_SPREAD = 0.45
MAX_TAKE_PROFIT_PCT = 0.85
STOP_LOSS_PCT = -1.50

MIN_REPEG_INTERVAL = 4.0
MIN_REPEG_TICKS = 3
BASE_URL = "https://api.mexc.com"
# ==============================================================

state = {
    "tick_size": 0.000001,
    "price_decimals": 6,
    "qty_decimals": 2,
    "mexc_bids": [],
    "mexc_asks": [],
    "btc_price": 0.0,
    "btc_10s_change": 0.0,
    "usdt_free": 0.0,
    "usdt_total": 0.0,
    "coin_total": 0.0,
    "coin_value_usd": 0.0,
    "bot_mode": "LOOKING_TO_BUY",
    "active_order_id": None,
    "active_order_side": None,
    "active_order_price": 0.0,
    "active_order_qty": 0.0,
    "entry_price": 0.0,
    "last_repeg_time": 0.0,
    "start_usdt": 0.0,
    "realized_pnl_usd": 0.0,
    "completed_cycles": 0,
    "repeg_count": 0,
    "status": "Ініціалізація...",
    "status_style": "yellow",
    "logs": []
}

btc_history = []


def log_event(msg: str):
    t_str = time.strftime("%H:%M:%S")
    state["logs"].insert(0, f"[{t_str}] {msg}")
    if len(state["logs"]) > 8:
        state["logs"].pop()


def floor_qty(val: float, decimals: int) -> float:
    factor = 10 ** decimals
    return math.floor(val * factor) / factor


def sign_params(params: dict) -> str:
    query_string = urlencode(params)
    signature = hmac.new(
        SECRET_KEY.strip().encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{query_string}&signature={signature}"


async def mexc_private_request(client: httpx.AsyncClient, method: str, endpoint: str, params: dict = None):
    """Безпечний запит до приватного API MEXC, який ніколи не падає на порожній відповіді."""
    if params is None:
        params = {}
    params["timestamp"] = int(time.time() * 1000)
    params["recvWindow"] = 10000
    signed_query = sign_params(params)
    url = f"{BASE_URL}{endpoint}?{signed_query}"
    headers = {"X-MEXC-APIKEY": API_KEY.strip(), "Content-Type": "application/json"}
    try:
        resp = await client.request(method, url, headers=headers)
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
        return resp.status_code, data
    except Exception as e:
        return 500, {"msg": str(e)}


async def fetch_symbol_rules(client: httpx.AsyncClient):
    resp = await client.get(f"{BASE_URL}/api/v3/exchangeInfo", params={"symbol": SYMBOL})
    if resp.status_code == 200:
        symbols = resp.json().get("symbols", [])
        if symbols:
            s = symbols[0]
            p_prec = int(s.get("quoteAssetPrecision", 6))
            q_prec = int(s.get("baseAssetPrecision", 2))
            state["price_decimals"] = p_prec
            state["qty_decimals"] = q_prec
            state["tick_size"] = 10 ** (-p_prec)
            log_event(f"Правила {SYMBOL}: Ціна {p_prec} знаків, Кількість {q_prec} знаків")


async def fetch_last_buy_price(client: httpx.AsyncClient) -> float:
    """Автоматично дістає точну ціну нашої останньої покупки з історії акаунта MEXC!"""
    code, trades = await mexc_private_request(client, "GET", "/api/v3/myTrades", {"symbol": SYMBOL, "limit": 5})
    if code == 200 and isinstance(trades, list) and trades:
        for t in reversed(trades):
            if t.get("isBuyer"):
                return float(t["price"])
    return 0.0


async def cancel_all_symbol_orders(client: httpx.AsyncClient):
    await mexc_private_request(client, "DELETE", "/api/v3/openOrders", {"symbol": SYMBOL})
    state["active_order_id"] = None
    state["active_order_price"] = 0.0
    state["active_order_qty"] = 0.0
    await asyncio.sleep(0.15)


async def sync_wallet_and_orders(client: httpx.AsyncClient):
    code, acc = await mexc_private_request(client, "GET", "/api/v3/account")
    if code != 200 or not isinstance(acc, dict) or "balances" not in acc:
        log_event(f"❌ Помилка API ключа/гаманця (Код {code}): {acc}")
        return

    usdt_free, usdt_locked = 0.0, 0.0
    coin_free, coin_locked = 0.0, 0.0
    for b in acc.get("balances", []):
        if b["asset"] == "USDT":
            usdt_free = float(b["free"])
            usdt_locked = float(b["locked"])
        elif b["asset"] == BASE_ASSET:
            coin_free = float(b["free"])
            coin_locked = float(b["locked"])

    state["usdt_free"] = usdt_free
    state["usdt_total"] = usdt_free + usdt_locked
    state["coin_total"] = coin_free + coin_locked

    if state["start_usdt"] == 0.0 and state["usdt_total"] > 0 and state["coin_total"] == 0:
        state["start_usdt"] = state["usdt_total"]

    best_bid = state["mexc_bids"][0][0] if state["mexc_bids"] else state["entry_price"]
    state["coin_value_usd"] = state["coin_total"] * best_bid if best_bid > 0 else 0.0

    if state["coin_value_usd"] >= MIN_NOTIONAL_USD:
        if state["bot_mode"] != "HOLDING_INVENTORY":
            await cancel_all_symbol_orders(client)
            if state["entry_price"] == 0.0:
                last_p = await fetch_last_buy_price(client)
                state["entry_price"] = last_p if last_p > 0 else (state["active_order_price"] or best_bid)
            state["bot_mode"] = "HOLDING_INVENTORY"
            state["last_repeg_time"] = 0.0
            log_event(
                f"✅ У ГАМАНЦІ: {state['coin_total']} {BASE_ASSET} (~${state['coin_value_usd']:.2f}) | "
                f"Ціна покупки з історії: {state['entry_price']:.{state['price_decimals']}f}"
            )
    else:
        if state["bot_mode"] == "HOLDING_INVENTORY":
            await cancel_all_symbol_orders(client)
            state["completed_cycles"] += 1
            if state["start_usdt"] > 0:
                state["realized_pnl_usd"] = state["usdt_total"] - state["start_usdt"]
            log_event(f"💰 ПРОДАНО! Загальний USDT: ${state['usdt_total']:.3f} (Кіл: {state['completed_cycles']})")
            state["bot_mode"] = "LOOKING_TO_BUY"
            state["entry_price"] = 0.0
            state["last_repeg_time"] = 0.0


async def place_maker_order(client: httpx.AsyncClient, side: str, price: float, qty: float,
                            order_type: str = "LIMIT_MAKER"):
    p_str = f"{price:.{state['price_decimals']}f}"
    q_str = f"{qty:.{state['qty_decimals']}f}"
    params = {
        "symbol": SYMBOL,
        "side": side,
        "type": order_type,
        "quantity": q_str,
        "price": p_str
    }
    code, res = await mexc_private_request(client, "POST", "/api/v3/order", params)
    if code == 200 and isinstance(res, dict) and "orderId" in res:
        state["active_order_id"] = res["orderId"]
        state["active_order_side"] = side
        state["active_order_price"] = price
        state["active_order_qty"] = qty
        state["last_repeg_time"] = time.time()
        state["repeg_count"] += 1
        log_event(f"📌 [{side}] Виставлено: {q_str} {BASE_ASSET} по {p_str} (${price * qty:.2f})")
        return True
    else:
        log_event(f"⚠️ Відхилено ({side} {p_str}): {res}")
        return False


def pick_smart_wall(levels: list, threshold_usd: float, ignore_price: float, ignore_qty: float) -> tuple[float, int]:
    if not levels:
        return 0.0, 0
    for idx, (price, qty) in enumerate(levels):
        eff_qty = qty
        if ignore_price > 0 and abs(price - ignore_price) < 1e-8:
            eff_qty = max(0.0, qty - ignore_qty)
        if price * eff_qty >= threshold_usd:
            return price, idx + 1
    return levels[-1][0], len(levels)


def should_repeg(new_price: float) -> bool:
    if state["active_order_id"] is None or state["active_order_price"] == 0.0:
        return True
    if time.time() - state["last_repeg_time"] < MIN_REPEG_INTERVAL:
        return False
    diff_ticks = abs(new_price - state["active_order_price"]) / state["tick_size"]
    return diff_ticks >= MIN_REPEG_TICKS


async def execute_bot_strategy(client: httpx.AsyncClient):
    if not state["mexc_bids"] or not state["mexc_asks"]:
        return

    tick = state["tick_size"]
    p_prec = state["price_decimals"]
    q_prec = state["qty_decimals"]
    best_bid = state["mexc_bids"][0][0]
    best_ask = state["mexc_asks"][0][0]

    my_p = state["active_order_price"]
    my_q = state["active_order_qty"]

    ref_bid, bid_lvl = pick_smart_wall(state["mexc_bids"], DUST_THRESHOLD_USD, my_p, my_q)
    ref_ask, _ = pick_smart_wall(state["mexc_asks"], DUST_THRESHOLD_USD, my_p, my_q)

    if state["bot_mode"] == "LOOKING_TO_BUY":
        if state["btc_10s_change"] <= -0.15:
            if state["active_order_id"]:
                await cancel_all_symbol_orders(client)
                log_event(f"🚨 PANIC: BTC летить вниз ({state['btc_10s_change']:.2f}%)!")
            state["status"] = f"🚨 PANIC: BTC падає ({state['btc_10s_change']:.2f}%). Поза ринком!"
            state["status_style"] = "bold white on red"
            return

        target_buy = round(ref_bid + tick, p_prec)
        if target_buy >= best_ask:
            target_buy = best_bid

        pot_sell = round(ref_ask - tick, p_prec)
        pot_spread = ((pot_sell - target_buy) / target_buy) * 100

        if pot_spread < MIN_PROFIT_SPREAD:
            if state["active_order_id"]:
                cur_spread = ((pot_sell - state["active_order_price"]) / state["active_order_price"]) * 100
                if cur_spread < MIN_PROFIT_SPREAD:
                    await cancel_all_symbol_orders(client)
                    log_event(f"⏸ Зняли BUY: спред стиснувся до {cur_spread:.2f}%")
            state["status"] = (
                f"⏸ Не женемося за ботом на #{bid_lvl} (спред там {pot_spread:.2f}%). "
                f"Наш ордер: {state['active_order_price']:.{p_prec}f}"
            )
            state["status_style"] = "yellow"
            return

        if should_repeg(target_buy):
            await cancel_all_symbol_orders(client)
            usd_to_spend = min(ORDER_SIZE_USD, state["usdt_total"] * 0.98)
            if usd_to_spend >= MIN_NOTIONAL_USD:
                buy_qty = floor_qty(usd_to_spend / target_buy, q_prec)
                ok = await place_maker_order(client, "BUY", target_buy, buy_qty, "LIMIT_MAKER")
                if ok:
                    state["entry_price"] = target_buy
            else:
                log_event(f"⚠️ Чекаємо розморозки або балансу USDT (Зараз: ${state['usdt_total']:.2f})")

        state["status"] = (
            f"🟢 СТОЇТЬ БОЙОВИЙ BUY ПО: {state['active_order_price']:.{p_prec}f} (перед #{bid_lvl}) | "
            f"Очікуваний спред: +{pot_spread:.2f}%"
        )
        state["status_style"] = "bold green"

    elif state["bot_mode"] == "HOLDING_INVENTORY":
        cur_pnl_pct = ((best_bid - state["entry_price"]) / state["entry_price"]) * 100 if state[
                                                                                              "entry_price"] > 0 else 0.0

        if cur_pnl_pct <= STOP_LOSS_PCT:
            log_event(f"🛑 STOP-LOSS ({cur_pnl_pct:.2f}%): Виходимо по Best Bid ({best_bid})!")
            await cancel_all_symbol_orders(client)
            sell_qty = floor_qty(state["coin_total"], q_prec)
            await place_maker_order(client, "SELL", best_bid, sell_qty, "LIMIT")
            return

        min_prof_sell = round(state["entry_price"] * (1 + MIN_PROFIT_SPREAD / 100.0), p_prec)
        max_cap_sell = round(state["entry_price"] * (1 + MAX_TAKE_PROFIT_PCT / 100.0), p_prec)
        front_ask_sell = round(best_ask - tick, p_prec)

        smart_sell = max(min_prof_sell, min(front_ask_sell, max_cap_sell))
        if smart_sell <= best_bid:
            smart_sell = round(best_bid + tick, p_prec)

        sell_qty = floor_qty(state["coin_total"], q_prec)

        if should_repeg(smart_sell) and sell_qty > 0:
            await cancel_all_symbol_orders(client)
            await place_maker_order(client, "SELL", smart_sell, sell_qty, "LIMIT_MAKER")

        exp_pct = ((state["active_order_price"] - state["entry_price"]) / state["entry_price"]) * 100 if state[
                                                                                                             "active_order_price"] and \
                                                                                                         state[
                                                                                                             "entry_price"] else 0.0
        state["status"] = (
            f"🟠 ПРОДАЄМО {sell_qty} {BASE_ASSET} ПО: {state['active_order_price']:.{p_prec}f} "
            f"(Вхід: {state['entry_price']:.{p_prec}f} | Ціль: +{exp_pct:.2f}%)"
        )
        state["status_style"] = "bold cyan"


async def trading_engine_loop():
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            await fetch_symbol_rules(client)
            await cancel_all_symbol_orders(client)

            while True:
                try:
                    d_resp = await client.get(f"{BASE_URL}/api/v3/depth", params={"symbol": SYMBOL, "limit": 6})
                    if d_resp.status_code == 200:
                        d_data = d_resp.json()
                        state["mexc_bids"] = [[float(p), float(q)] for p, q in d_data.get("bids", [])]
                        state["mexc_asks"] = [[float(p), float(q)] for p, q in d_data.get("asks", [])]

                    await sync_wallet_and_orders(client)
                    await execute_bot_strategy(client)
                except Exception as e:
                    log_event(f"⚠ Помилка в циклі: {e}")
                await asyncio.sleep(0.7)
        except asyncio.CancelledError:
            pass
        finally:
            await cancel_all_symbol_orders(client)


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
    p_prec = state["price_decimals"]
    header = Text.from_markup(
        f"Всього USDT: [bold green]${state['usdt_total']:.2f}[/bold green] (Вільні: ${state['usdt_free']:.2f}) | "
        f"В монеті {BASE_ASSET}: [bold yellow]{state['coin_total']} (~${state['coin_value_usd']:.2f})[/bold yellow] | "
        f"PnL: [bold green]{state['realized_pnl_usd']:+.3f}$[/bold green] (Кіл: {state['completed_cycles']}) | "
        f"BTC: ${state['btc_price']:,.0f}\n"
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

        b_mark = " ⬅ [bold yellow]НАШ ОРДЕР[/bold yellow]" if (
                    state["active_order_side"] == "BUY" and abs(b_p - state["active_order_price"]) < 1e-8) else ""
        a_mark = " ⬅ [bold cyan]НАШ ТЕЙК[/bold cyan]" if (
                    state["active_order_side"] == "SELL" and abs(a_p - state["active_order_price"]) < 1e-8) else ""

        table.add_row(
            f"#{i + 1}",
            f"${b_p * b_q:,.1f}" if b_p else "-",
            f"{b_p:.{p_prec}f}{b_mark}" if b_p else "-",
            f"{a_p:.{p_prec}f}{a_mark}" if a_p else "-",
            f"${a_p * a_q:,.1f}" if a_p else "-"
        )

    logs_str = "\n".join(state["logs"]) if state["logs"] else "Підключення до приватного API MEXC..."
    logs_panel = Panel(logs_str, title="⚡ Бойовий журнал (Реальні ордери та Гаманець)", border_style="yellow")

    return Panel(Group(header, table, logs_panel), title=f"LIVE MEXC BOT [{SYMBOL}] (Ордер ${ORDER_SIZE_USD})",
                 border_style="red")


async def main():
    console = Console()
    tasks = [
        asyncio.create_task(trading_engine_loop()),
        asyncio.create_task(binance_btc_guard())
    ]
    with Live(render_ui(), refresh_per_second=5, console=console) as live:
        try:
            while True:
                live.update(render_ui())
                await asyncio.sleep(0.2)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Зупинка бота... Знімаємо відкриті ордери з біржі![/bold yellow]")
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            console.print("[bold green]✅ Всі ордери успішно скасовано. Можна закривати термінал.[/bold green]")


if __name__ == "__main__":
    asyncio.run(main())