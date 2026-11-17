"""Demo run on synthetic prices. Paper trading only."""
import math

from bot.agents import MarketDataAgent, SignalAgent, RiskAgent, PaperExecutionAgent
from bot.orchestrator import run_pipeline


def fake_prices(symbol: str, n: int) -> list[float]:
    # Synthetic sine-wave prices, so the demo is reproducible and offline.
    base = 100 + 10 * math.sin(len(symbol))
    return [base + 5 * math.sin(i / 3) for i in range(n)]


def main() -> None:
    ctx = {
        "symbols": ["AAA", "BBB"],
        "portfolio": {"cash": 10_000.0, "positions": {}},
    }
    pipeline = [
        MarketDataAgent(fake_prices),
        SignalAgent(),
        RiskAgent(),
        PaperExecutionAgent(),
    ]
    result = run_pipeline(pipeline, ctx)
    print("Signals:", [(s.symbol, s.side, s.reason) for s in result["signals"]])
    print("Orders:", result["orders"])
    print("Portfolio:", result["portfolio"])


if __name__ == "__main__":
    main()
