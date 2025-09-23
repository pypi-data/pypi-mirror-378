# Copyright (C) 2025 Codeligence
#
# This file is part of Dev Agents.
#
# Dev Agents is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dev Agents is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Dev Agents.  If not, see <https://www.gnu.org/licenses/>.


from pathlib import Path
from typing import Any, cast

from core.project_config import ProjectConfig


class GitRepositoryConfig:
    """Git repository specific configuration class."""

    def __init__(self, config_data: dict[str, Any]):
        """Initialize with git configuration data.

        Args:
            config_data: Git configuration dictionary
        """
        self._config_data = config_data or {}

    @classmethod
    def from_project_config(
        cls, project_config: ProjectConfig
    ) -> "GitRepositoryConfig":
        """Create from project configuration.

        Args:
            project_config: ProjectConfig instance

        Returns:
            GitRepositoryConfig instance
        """
        config_data = project_config.get_git_config()
        return cls(config_data)

    def get_repo_dir(self) -> str:
        """Get the git repository directory path.

        Priority order:
        1. Configuration file setting (path)
        2. Current working directory (fallback)

        Returns:
            Absolute path to the git repository
        """
        repo_path = self._config_data.get("path")

        if repo_path:
            return str(Path(repo_path).resolve())

        # Fallback to current directory
        return str(Path().resolve())

    def get_default_branch(self) -> str:
        """Get the default branch name (default: 'main')."""
        return cast("str", self._config_data.get("defaultBranch", "main"))

    def get_auto_pull(self) -> bool:
        """Get auto-pull setting for repository updates."""
        auto_pull = self._config_data.get("autoPull", "false")
        if isinstance(auto_pull, bool):
            return auto_pull
        return str(auto_pull).lower() in ("true", "1", "yes", "on")

    def get_pull_interval_seconds(self) -> int:
        """Get the pull interval in seconds to prevent excessive pulls.

        Returns:
            Number of seconds to wait between automatic pulls (default: 120)
        """
        interval = self._config_data.get("pullIntervalSeconds", 120)
        return int(interval)

    def is_configured(self) -> bool:
        """Check if git repository is properly configured.

        Returns:
            True if repo path exists and is a valid directory
        """
        repo_path = Path(self.get_repo_dir())
        return repo_path.exists() and repo_path.is_dir()
