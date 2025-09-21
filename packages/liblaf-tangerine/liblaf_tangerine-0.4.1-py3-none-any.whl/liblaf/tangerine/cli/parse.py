from pathlib import Path
from typing import Annotated

import cappa
from cappa import Arg


@cappa.command(invoke="liblaf.tangerine.cli.invoke.run")
class Args:
    files: Annotated[list[Path], Arg(default=cappa.ValueFrom(list))]
    in_place: Annotated[bool, Arg(long=True, default=False)]
