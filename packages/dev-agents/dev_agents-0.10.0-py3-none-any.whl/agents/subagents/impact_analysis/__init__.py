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


"""Impact Analysis Subagent

This subagent analyzes code changes to determine potential UI and API impacts.
It uses CodeResearchAgent instances to analyze frontend and backend changes separately.
"""

from .impact_analysis_subagent import ImpactAnalysisSubagent
from .models import (
    ApiChange,
    ApiImpactReport,
    ImpactAnalysisResult,
    UIComponent,
    UIImpactReport,
)

__all__ = [
    "UIComponent",
    "UIImpactReport",
    "ApiChange",
    "ApiImpactReport",
    "ImpactAnalysisResult",
    "ImpactAnalysisSubagent",
]
