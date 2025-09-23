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


from core.integrations import get_provider_registry

from .config import JiraConfig
from .provider import JiraIssueProvider

# Register Jira providers with the global registry
registry = get_provider_registry()
registry.register_issue_provider("jira", JiraIssueProvider.from_config)

__all__ = ["JiraIssueProvider", "JiraConfig"]
