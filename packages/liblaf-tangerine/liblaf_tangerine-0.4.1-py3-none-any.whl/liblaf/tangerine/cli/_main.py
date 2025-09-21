import asyncio

import cappa

from liblaf.tangerine._version import __version__

from .parse import Args


def main() -> None:
    asyncio.run(cappa.invoke_async(Args, version=__version__))
