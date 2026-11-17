"""Runs the agents in order and returns the final context."""
from typing import Iterable


def run_pipeline(agents: Iterable, ctx: dict) -> dict:
    for agent in agents:
        ctx = agent.run(ctx)
    return ctx
