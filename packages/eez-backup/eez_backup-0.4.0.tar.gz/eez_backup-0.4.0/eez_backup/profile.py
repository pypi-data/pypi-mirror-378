from contextlib import contextmanager
from itertools import chain
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Generator, List, Self

from pydantic import Field, ConfigDict

from eez_backup.command import Command
from eez_backup.base import BaseModel, Env
from eez_backup.repository import Repository

ProfileGenerator = Generator["Profile", None, None]


class InProfile(BaseModel):
    base: Path | None = None
    env: Env = Field(default_factory=Env)
    repositories: List[str] | None = None
    include: List[Path] | None = None
    exclude: List[Path] | None = None
    clean_policy: Dict[str, int] | None = None

    model_config = ConfigDict()

    def merge(self, other: "InProfile") -> "InProfile":
        new_profile = InProfile.model_validate(self.dump() | other.dump())
        new_profile.env = self.env | other.env
        if self.base and other.base and (new_base := self.base.joinpath(other.base)).is_dir():
            new_profile.base = new_base
        return new_profile

    def generate_profiles(
        self, repositories: Dict[str, Repository], default: Self | None = None, **kwargs
    ) -> ProfileGenerator:
        profile = default.merge(self) if default else self
        fields = profile.dump() | kwargs
        for repository in fields.pop("repositories", []):
            yield Profile(repository=repositories[repository], **fields)


class Profile(BaseModel):
    tag: str = Field(min_length=1)
    base: Path
    repository: Repository
    include: List[Path] = Field(min_length=1)
    exclude: List[Path] = Field(default_factory=list)
    clean_policy: Dict[str, int]
    env: Env = Field(default_factory=Env)

    @property
    def identifier(self) -> str:
        return f"{self.tag}@{self.repository.tag}"

    def base_command(self, *args: str, **kwargs) -> Command:
        cmd = self.repository.base_command(*args, **kwargs)
        cmd.set_name(repr(self.identifier))
        cmd.set_cwd(self.base)
        cmd.update_env(self.env)
        return cmd

    @contextmanager
    def backup_cmd_context(self, **kwargs) -> Generator[Command, None, None]:
        cmd = self.base_command(**kwargs)
        cmd.set_name(f"Backup {self.identifier!r}")
        cmd.add_arg("backup")
        cmd.add_arg("-q")
        cmd.add_kwarg("--tag", self.tag)
        cmd.add_arg("--exclude-caches")

        with NamedTemporaryFile(mode="rt+") as f_incl, NamedTemporaryFile(mode="rt+") as f_excl:
            f_incl.write("\n".join(map(str, self.include)))
            f_excl.write("\n".join(map(str, self.exclude)))
            f_incl.flush()
            f_excl.flush()
            cmd.add_kwarg("--files-from", f_incl.name)
            cmd.add_kwarg("--exclude-file", f_excl.name)
            yield cmd

    def clean_cmd(self, **kwargs) -> Command:
        cmd = self.base_command(**kwargs)
        cmd.set_name(f"Clean {self.identifier!r}")
        cmd.add_arg("forget")
        cmd.add_kwarg("--tag", self.tag)
        cmd.add_args_from(map(str, chain(*self.clean_policy.items())))
        return cmd
