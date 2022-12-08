# Copyright (C) 2022 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from pontos.models import Model

__all__ = (
    "App",
    "GitHubModel",
    "User",
    "Team",
)


@dataclass(init=False)
class GitHubModel(Model):
    """
    Base class for all GitHub models
    """


@dataclass
class User(GitHubModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool


class TeamPrivacy(Enum):
    SECRET = "secret"
    CLOSED = "closed"


class TeamRole(Enum):
    MEMBER = "member"
    MAINTAINER = "maintainer"


class Permission(Enum):
    PULL = "pull"
    PUSH = "push"
    TRIAGE = "triage"
    MAINTAIN = "maintain"
    ADMIN = "admin"


@dataclass
class Team(GitHubModel):
    id: int
    node_id: str
    url: str
    html_url: str
    name: str
    slug: str
    description: str
    privacy: TeamPrivacy
    permission: Permission
    members_url: str
    repositories_url: str
    parent: Optional["Team"] = None


@dataclass
class App(GitHubModel):
    id: int
    slug: str
    node_id: str
    owner: User
    name: str
    description: str
    external_url: str
    html_url: str
    created_at: str
    updated_at: str
    events: List[str]
