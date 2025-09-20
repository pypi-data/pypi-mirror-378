from dataclasses import dataclass, field
from pathlib import Path
from re import sub
from tomllib import load

from click import Context, Parameter


@dataclass
class WorkDir:
    project: Path
    pyproject_toml: Path = field(init=False)
    workflows: Path = field(init=False)
    helper_script: Path = field(init=False)
    build: Path = field(init=False)
    release: Path = field(init=False)
    test_e2e: Path = field(init=False)

    def __post_init__(self):
        self.pyproject_toml = self.project / "pyproject.toml"
        self.workflows = self.project / ".github" / "workflows"
        self.helper_script = self.workflows / "verify-upstream-has-not-changed.sh"
        self.build = self.workflows / "build.yml"
        self.release = self.workflows / "release.yml"
        self.test_e2e = self.workflows / "test-e2e.yml"


def set_workdir(ctx: Context, _param: Parameter, path: Path) -> WorkDir:
    return WorkDir(path)


def normalize(name: str) -> str:
    return sub(r"[-_.]+", "_", name).lower()


def get_project_name(pyproject_toml_path: Path) -> str:
    pyproject_toml: dict = load(pyproject_toml_path.open("rb"))
    project_name = pyproject_toml["project"]["name"]
    return project_name


def set_module_name(pyproject_toml_path: Path, module_name: str | None) -> str:
    if not module_name:
        package_name = get_project_name(pyproject_toml_path)
        module_name = normalize(package_name)
        return module_name
    return normalize(module_name)
