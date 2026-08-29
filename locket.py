#!/usr/bin/env python
"""Safe command-line entrypoint for the zlocket workflow simulator."""

from zlocket.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
