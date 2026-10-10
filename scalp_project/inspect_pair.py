import asyncio
import httpx
from rich.console import Console
from rich.table import Table

SYMBOL = "ZZZUSDT"  # Можна підставити ZCATUSDT, HOOKRUSDT, ORBIOUSDT


async def inspect_microstructure(symbol: str):
    console = Console()
    async with httpx.AsyncClient(timeout=10.0) as client:
        depth_resp, trades_resp = await asyncio.gather(
            client.get("https://api.mexc.com/api/v3/depth", params={"symbol": symbol, "limit": 5}),
            client.get("https://api.mexc.com/api/v3/trades", params={"symbol": symbol, "limit": 15})
        )
        depth = depth_resp.json()
        trades = trades_resp.json()

    bids = [[float(p), float(q)] for p, q in depth.get("bids", [])]
    asks = [[float(p), float(q)] for p, q in depth.get("asks", [])]

    if not bids or not asks:
        console.print("[red]Стакан порожній![/red]")
        return

    best_bid, best_ask = bids[0][0], asks[0][0]
    spread_pct = ((best_ask - best_bid) / best_bid) * 100

    console.print(f"\n[bold yellow]=== Рентген пари {symbol} ===[/bold yellow]")
    console.print(f"Best Bid: [green]{best_bid}[/green] (${best_bid * bids[0][1]:.1f}) | "
                  f"Best Ask: [red]{best_ask}[/red] (${best_ask * asks[0][1]:.1f}) | "
                  f"Спред: [bold magenta]{spread_pct:.2f}%[/bold magenta]\n")

    table = Table(title="Останні 15 угод (Аналіз виконання)")
    table.add_column("Ціна угоди", justify="right")
    table.add_column("Обсяг ($)", justify="right")
    table.add_column("Тип", justify="center")
    table.add_column("Де пройшла угода?", style="bold")

    inside_spread_count = 0
    edge_hit_count = 0

    for t in trades:
        price = float(t["price"])
        qty_usd = price * float(t["qty"])
        side = "[red]SELL (По Bid)[/red]" if t.get("isBuyerMaker") else "[green]BUY (По Ask)[/green]"

        # Перевіряємо, чи угода вдарила в реальний стакан, чи намальована всередині спреду
        if best_bid < price < best_ask:
            loc = "[yellow]ВСЕРЕДИНІ СПРЕДУ (Wash-бот)[/yellow]"
            inside_spread_count += 1
        elif price <= best_bid:
            loc = "[bold green]УДАР У BID (Наливають лімітку!)[/bold green]"
            edge_hit_count += 1
        else:
            loc = "[bold cyan]УДАР В ASK (Викуповують тейк!)[/bold cyan]"
            edge_hit_count += 1

        table.add_row(f"{price:.6g}", f"${qty_usd:.2f}", side, loc)

    console.print(table)

    if edge_hit_count >= inside_spread_count:
        console.print("\n[bold green]ВЕРДИКТ: Стакан ЖИВИЙ! Угоди реально б'ють по лімітках на краях.[/bold green]")
    else:
        console.print("\n[bold red]ВЕРДИКТ: Багато угод всередині спреду (працює бот малювання обсягу).[/bold red]")


if __name__ == "__main__":
    asyncio.run(inspect_microstructure(SYMBOL))

API_KEY = os.getenv("MEXC_API_KEY", "mx0vgl9L2kKo5v7hqW")
SECRET_KEY = os.getenv("MEXC_SECRET_KEY", "4502a4b2553244928c6170f46ae45624")