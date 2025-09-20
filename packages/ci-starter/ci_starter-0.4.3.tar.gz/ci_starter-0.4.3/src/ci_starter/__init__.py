from importlib.metadata import version as get_version
from logging import getLogger
from pathlib import Path

from .asset_getter import get_asset
from .git_helpers import get_repo_name
from .presets import DISTRIBUTION_ARTIFACTS_DIR
from .semantic_release_config import SemanticReleaseConfiguration

__version__ = get_version(__package__)

logger = getLogger(__name__)


def generate_semantic_release_config(project_repo_path: Path) -> None:
    repo_name = get_repo_name(project_repo_path)

    config = SemanticReleaseConfiguration(project_repo_path, repo_name, DISTRIBUTION_ARTIFACTS_DIR)
    config.write()


def generate_helper_script(script_path: Path) -> None:
    _create_dirs = script_path.parent.mkdir(parents=True, exist_ok=True)

    asset_path = Path(*script_path.parts[-2:])
    script: str = get_asset(asset_path)

    with script_path.open("w", encoding="utf-8") as script_file:
        script_file.write(script)
