from pathlib import Path

from portfolio.soundmatch import build

if __name__ == "__main__":
    print(build(Path("data/soundmatch")))
