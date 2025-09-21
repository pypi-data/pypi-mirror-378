import asyncio
import sys
from pathlib import Path

from liblaf.tangerine import core

from .parse import Args


async def run(self: Args) -> None:
    if not self.files:
        self.files = [Path("-")]
    env = core.Environment()
    await asyncio.gather(*(_process_file(env, file, args=self) for file in self.files))


def _read_text(file: Path) -> str:
    if file == Path("-"):
        return sys.stdin.read()
    return file.read_text()


async def _process_file(env: core.Environment, file: Path, args: Args) -> None:
    text: str = _read_text(file)
    segments: list[core.Segment] = env.parse(text)
    output: str = await env.render(segments)
    if args.in_place:
        file.write_text(output)
    else:
        print(output, end="")
