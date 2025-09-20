from pathlib import Path
from sys import version_info
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

OLD_PYTHON_MINOR_VERSION = 11

if version_info.minor == OLD_PYTHON_MINOR_VERSION:
    from importlib_resources import files
else:
    from importlib.resources import files


def get_asset(path: str) -> str:
    path = Path(path)
    asset: Traversable = files(f"{__package__}.assets")
    for path_segment in path.parts:
        asset = asset.joinpath(path_segment)
    result: str = asset.read_text(encoding="utf-8")
    return result
