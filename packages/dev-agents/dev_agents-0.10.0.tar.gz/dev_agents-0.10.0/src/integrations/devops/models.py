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


from typing import Any, cast
import re

from bs4 import BeautifulSoup


class DevOpsError(Exception):
    pass


class Person:
    def __init__(self, display_name: str | None, unique_name: str | None) -> None:
        self.display_name = display_name
        self.unique_name = unique_name

    def format(self) -> str:
        return f"{self.display_name} <{self.unique_name}>"


class WorkItem:
    def __init__(self, response_json: dict[str, Any]) -> None:
        self.data = response_json

    def get_system_team_project(self) -> str | None:
        return cast(
            "str | None", self.data.get("fields", {}).get("System.TeamProject", None)
        )

    def get_system_state(self) -> str | None:
        return cast("str | None", self.data.get("fields", {}).get("System.State", None))

    def get_system_reason(self) -> str | None:
        return cast(
            "str | None", self.data.get("fields", {}).get("System.Reason", None)
        )

    def get_system_created_date(self) -> str | None:
        return cast(
            "str | None", self.data.get("fields", {}).get("System.CreatedDate", None)
        )

    def get_system_created_by(self) -> Person:
        created_by = self.data.get("fields", {}).get("System.CreatedBy", {})
        return Person(
            display_name=created_by.get("displayName"),
            unique_name=created_by.get("uniqueName"),
        )

    def get_system_changed_date(self) -> str | None:
        return cast(
            "str | None", self.data.get("fields", {}).get("System.ChangedDate", None)
        )

    def get_system_changed_by(self) -> Person:
        changed_by = self.data.get("fields", {}).get("System.ChangedBy", {})
        return Person(
            display_name=changed_by.get("displayName"),
            unique_name=changed_by.get("uniqueName"),
        )

    def get_system_title(self) -> str | None:
        return cast("str | None", self.data.get("fields", {}).get("System.Title", None))

    def get_custom_application(self) -> str | None:
        return cast(
            "str | None", self.data.get("fields", {}).get("Custom.Application", None)
        )

    def get_custom_dev(self) -> Person:
        custom_dev = self.data.get("fields", {}).get("Custom.Dev", {})
        return Person(
            display_name=custom_dev.get("displayName"),
            unique_name=custom_dev.get("uniqueName"),
        )

    def get_custom_feature_id(self) -> str | None:
        return cast(
            "str | None", self.data.get("fields", {}).get("Custom.FeatureId", None)
        )

    def get_system_description(self) -> str | None:
        return cast(
            "str | None", self.data.get("fields", {}).get("System.Description", None)
        )

    def get_system_description_plain(self) -> str:
        """
        Return the system description with all HTML tags removed using BeautifulSoup.
        Content within strike-through tags (<strike>, <s>, <del>) is removed entirely.

        Returns:
            str: Plain text description without HTML tags and strike-through content
        """
        description = self.get_system_description()
        if not description:
            return ""

        # Use BeautifulSoup to parse HTML
        soup = BeautifulSoup(description, "html.parser")

        # Remove all content within strike-through tags
        for strike_tag in soup.find_all(["strike", "s", "del"]):
            strike_tag.decompose()

        # Extract text from remaining content
        clean_text = soup.get_text(separator=" ", strip=True)

        # Remove extra whitespace
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        return clean_text

    def get_relation_urls(self) -> list[str]:
        return [relation.get("url") for relation in self.data.get("relations", [])]

    def get_commit_hashes(self) -> list[str]:
        urls = self.get_relation_urls()
        commit_hashes = []

        for url in urls:
            if "Commit" in url:
                # Replace %2f with / and split by /
                url = url.lower().replace("%2f", "/")
                # Get the last element which is the commit hash
                commit_hash = url.split("/")[-1]
                commit_hashes.append(commit_hash)

        return commit_hashes

    def get_pull_request_ids(self) -> list[str]:
        urls = self.get_relation_urls()
        pull_request_ids = []

        for url in urls:
            if "PullRequestId" in url:
                # Replace %2f with / and split by /
                url = url.lower().replace("%2f", "/")
                # Get the last element which is the commit hash
                pull_request_id = url.split("/")[-1]
                pull_request_ids.append(pull_request_id)

        return pull_request_ids

    def get_description_images(self) -> list[str]:
        """Extract image URLs from the HTML description"""
        description = self.get_system_description()
        if not description:
            return []

        # Use regex to find all img tags and extract the src attribute
        img_pattern = r'<img\s+[^>]*src="([^"]+)"[^>]*>'
        return re.findall(img_pattern, description)

    def get_composed_work_item_info(self) -> str:
        """Return a formatted string with all work item information"""
        info = f"Title: {self.get_system_title()}\n"
        info += f"Description: {self.get_system_description_plain()}\n"
        info += f"Team Project: {self.get_system_team_project()}\n"
        info += f"State: {self.get_system_state()}\n"
        info += f"Reason: {self.get_system_reason()}\n"
        info += f"Created Date: {self.get_system_created_date()}\n"
        info += f"Created By: {self.get_system_created_by().format()}\n"
        info += f"Changed Date: {self.get_system_changed_date()}\n"
        info += f"Changed By: {self.get_system_changed_by().format()}\n"
        info += f"Application: {self.get_custom_application()}\n"
        info += f"Dev: {self.get_custom_dev().format()}\n"
        info += f"Feature ID: {self.get_custom_feature_id()}\n"
        return info


class PullRequest:
    def __init__(
        self, pr_data: dict[str, Any], commit_data: list[dict[str, Any]]
    ) -> None:
        self.pr = pr_data
        self.commit_data = commit_data

    def get_composed_PR_info(self) -> str:
        # Extracting the most important information from the pull request data
        id = self.pr.get("pullRequestId", "Missing PR ID")
        title = self.pr.get("title", "No Title")
        status = self.pr.get("status", "No Status")
        created_by = self.pr.get("createdBy", {}).get("displayName", "Unknown")
        creation_date = self.pr.get("creationDate", "Unknown")
        closed_date = self.pr.get("closedDate", "Unknown")
        source_branch = self.pr.get("sourceRefName", "Unknown")
        target_branch = self.pr.get("targetRefName", "Unknown")
        description = self.pr.get("description", "No Description")

        # Format the information into a readable string
        formatted_info = (
            f"Pull Request ID: {id}\n"
            f"Title: {title}\n"
            f"Status: {status}\n"
            f"Created By: {created_by}\n"
            f"Creation Date: {creation_date}\n"
            f"Closed Date: {closed_date}\n"
            f"Source Branch: {source_branch}\n"
            f"Target Branch: {target_branch}\n"
            f"Description:\n{description}\n"
        )
        return formatted_info

    def get_commit_hashes(self) -> list[str]:
        # Extract commit hashes from the commit data
        if isinstance(self.commit_data, dict):
            commit_hashes = [
                commit["commitId"] for commit in self.commit_data.get("value", [])
            ]
        else:
            commit_hashes = [commit["commitId"] for commit in self.commit_data]
        return commit_hashes

    def get_source_branch(self) -> str:
        """Get the source branch name with 'refs/heads/' prefix removed if present."""
        source_branch = cast("str", self.pr.get("sourceRefName", ""))
        if source_branch.startswith("refs/heads/"):
            source_branch = source_branch[11:]  # Remove 'refs/heads/' prefix
        return source_branch

    def get_target_branch(self) -> str:
        """Get the target branch name with 'refs/heads/' prefix removed if present."""
        target_branch = cast("str", self.pr.get("targetRefName", ""))
        if target_branch.startswith("refs/heads/"):
            target_branch = target_branch[11:]  # Remove 'refs/heads/' prefix
        return target_branch

    def get_source_commit_id(self) -> str:
        """Get the commit ID of the last merge source commit."""
        source_commit = self.pr.get("lastMergeSourceCommit", {})
        return cast("str", source_commit.get("commitId", ""))

    def get_target_commit_id(self) -> str:
        """Get the commit ID of the last merge target commit."""
        target_commit = self.pr.get("lastMergeTargetCommit", {})
        return cast("str", target_commit.get("commitId", ""))

    def get_merge_commit_id(self) -> str:
        """Get the commit ID of the last merge target commit."""
        target_commit = self.pr.get("lastMergeCommit", {})
        return cast("str", target_commit.get("commitId", ""))
