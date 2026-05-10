"""Uruchomienie okna gry Snake z AI (BFS)."""
from __init__ import (
    BFS_RETRY_EVERY_MOVES,
    CELL,
    DELAY_MS,
    GRID_H,
    GRID_W,
    LOGS,
    SNAKE_LEN,
)
from snake_game import SnakeGame


def main() -> int:
    game = SnakeGame(
        grid_w=GRID_W,
        grid_h=GRID_H,
        snake_len=SNAKE_LEN,
        delay_ms=DELAY_MS,
        cell_px=CELL,
        bfs_retry_every_moves=BFS_RETRY_EVERY_MOVES,
        logs=LOGS,
    )
    game.run_game()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
