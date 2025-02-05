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

# pylint: disable=too-many-lines, redefined-builtin, line-too-long

import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import httpx

from pontos.github.api import GitHubRESTApi
from pontos.github.api.workflows import GitHubAsyncRESTWorkflows
from tests import AsyncIteratorMock, aiter, anext
from tests.github.api import (
    GitHubAsyncRESTTestCase,
    create_response,
    default_request,
)

here = Path(__file__).parent


class GitHubAsyncRESTWorkflowsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTWorkflows

    async def test_get(self):
        response = create_response()
        response.json.return_value = {
            "id": 1,
            "node_id": "MDg6V29ya2Zsb3cxNjEzMzU=",
            "name": "CI",
            "path": ".github/workflows/blank.yaml",
            "state": "active",
            "created_at": "2020-01-08T23:48:37.000-08:00",
            "updated_at": "2020-01-08T23:50:21.000-08:00",
            "url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/161335",
            "html_url": "https://github.com/octo-org/octo-repo/blob/master/.github/workflows/161335",
            "badge_url": "https://github.com/octo-org/octo-repo/workflows/CI/badge.svg",
        }
        self.client.get.return_value = response

        workflow = await self.api.get("foo/bar", "ci.yml")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml"
        )

        self.assertEqual(workflow.id, 1)

    async def test_get_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get("foo/bar", "ci.yml")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml"
        )

    async def test_get_all(self):
        response1 = create_response()
        response1.json.return_value = {
            "workflows": [
                {
                    "id": 1,
                    "node_id": "MDg6V29ya2Zsb3cxNjEzMzU=",
                    "name": "CI",
                    "path": ".github/workflows/blank.yaml",
                    "state": "active",
                    "created_at": "2020-01-08T23:48:37.000-08:00",
                    "updated_at": "2020-01-08T23:50:21.000-08:00",
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/161335",
                    "html_url": "https://github.com/octo-org/octo-repo/blob/master/.github/workflows/161335",
                    "badge_url": "https://github.com/octo-org/octo-repo/workflows/CI/badge.svg",
                }
            ]
        }
        response2 = create_response()
        response2.json.return_value = {
            "workflows": [
                {
                    "id": 2,
                    "node_id": "MDg6V29ya2Zsb3cxNjEzMzU=",
                    "name": "CI",
                    "path": ".github/workflows/blank.yaml",
                    "state": "active",
                    "created_at": "2020-01-08T23:48:37.000-08:00",
                    "updated_at": "2020-01-08T23:50:21.000-08:00",
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/161335",
                    "html_url": "https://github.com/octo-org/octo-repo/blob/master/.github/workflows/161335",
                    "badge_url": "https://github.com/octo-org/octo-repo/workflows/CI/badge.svg",
                },
                {
                    "id": 3,
                    "node_id": "MDg6V29ya2Zsb3cxNjEzMzU=",
                    "name": "CI",
                    "path": ".github/workflows/blank.yaml",
                    "state": "active",
                    "created_at": "2020-01-08T23:48:37.000-08:00",
                    "updated_at": "2020-01-08T23:50:21.000-08:00",
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/161335",
                    "html_url": "https://github.com/octo-org/octo-repo/blob/master/.github/workflows/161335",
                    "badge_url": "https://github.com/octo-org/octo-repo/workflows/CI/badge.svg",
                },
            ]
        }

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.get_all("foo/bar"))
        workflow = await anext(async_it)
        self.assertEqual(workflow.id, 1)
        workflow = await anext(async_it)
        self.assertEqual(workflow.id, 2)
        workflow = await anext(async_it)
        self.assertEqual(workflow.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/actions/workflows",
            params={"per_page": "100"},
        )

    async def test_get_workflow_runs(self):
        response1 = create_response()
        response1.json.return_value = {
            "workflow_runs": [
                {
                    "id": 1,
                    "name": "Build",
                    "node_id": "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==",
                    "check_suite_id": 42,
                    "check_suite_node_id": "MDEwOkNoZWNrU3VpdGU0Mg==",
                    "head_branch": "master",
                    "head_sha": "acb5820ced9479c074f688cc328bf03f341a511d",
                    "run_number": 562,
                    "event": "push",
                    "status": "queued",
                    "conclusion": None,
                    "workflow_id": 159038,
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
                    "html_url": "https://github.com/octo-org/octo-repo/actions/runs/30433642",
                    "pull_requests": [],
                    "created_at": "2020-01-22T19:33:08Z",
                    "updated_at": "2020-01-22T19:33:08Z",
                    "actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "run_attempt": 1,
                    "run_started_at": "2020-01-22T19:33:08Z",
                    "triggering_actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
                    "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
                    "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
                    "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
                    "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
                    "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
                    "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
                    "head_commit": {
                        "id": "acb5820ced9479c074f688cc328bf03f341a511d",
                        "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
                        "message": "Create linter.yaml",
                        "timestamp": "2020-01-22T19:33:05Z",
                        "author": {
                            "name": "Octo Cat",
                            "email": "octocat@github.com",
                        },
                        "committer": {
                            "name": "GitHub",
                            "email": "noreply@github.com",
                        },
                    },
                    "repository": {
                        "id": 1296269,
                        "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                        "name": "Hello-World",
                        "full_name": "octocat/Hello-World",
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "private": False,
                        "html_url": "https://github.com/octocat/Hello-World",
                        "description": "This your first repo!",
                        "fork": False,
                        "url": "https://api.github.com/repos/octocat/Hello-World",
                        "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                        "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                        "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                        "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                        "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                        "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                        "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                        "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                        "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                        "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                        "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                        "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                        "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                        "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                        "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                        "git_url": "git:github.com/octocat/Hello-World.git",
                        "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                        "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                        "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                        "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                        "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                        "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                        "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                        "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                        "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                        "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                        "ssh_url": "git@github.com:octocat/Hello-World.git",
                        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                        "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                        "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                        "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                        "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                        "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                        "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks",
                    },
                    "head_repository": {
                        "id": 217723378,
                        "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
                        "name": "octo-repo",
                        "full_name": "octo-org/octo-repo",
                        "private": True,
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "html_url": "https://github.com/octo-org/octo-repo",
                        "description": None,
                        "fork": False,
                        "url": "https://api.github.com/repos/octo-org/octo-repo",
                        "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
                        "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
                        "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
                        "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
                        "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
                        "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
                        "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
                        "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
                        "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
                        "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
                        "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
                        "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
                        "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
                        "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
                        "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
                        "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
                        "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
                        "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
                        "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
                        "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
                        "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
                        "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
                        "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
                        "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
                        "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
                        "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
                        "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
                        "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
                        "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
                        "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
                        "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
                        "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
                        "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
                    },
                }
            ]
        }
        response2 = create_response()
        response2.json.return_value = {
            "workflow_runs": [
                {
                    "id": 2,
                    "name": "Build",
                    "node_id": "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==",
                    "check_suite_id": 42,
                    "check_suite_node_id": "MDEwOkNoZWNrU3VpdGU0Mg==",
                    "head_branch": "master",
                    "head_sha": "acb5820ced9479c074f688cc328bf03f341a511d",
                    "run_number": 562,
                    "event": "push",
                    "status": "queued",
                    "conclusion": None,
                    "workflow_id": 159038,
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
                    "html_url": "https://github.com/octo-org/octo-repo/actions/runs/30433642",
                    "pull_requests": [],
                    "created_at": "2020-01-22T19:33:08Z",
                    "updated_at": "2020-01-22T19:33:08Z",
                    "actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "run_attempt": 1,
                    "run_started_at": "2020-01-22T19:33:08Z",
                    "triggering_actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
                    "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
                    "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
                    "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
                    "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
                    "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
                    "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
                    "head_commit": {
                        "id": "acb5820ced9479c074f688cc328bf03f341a511d",
                        "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
                        "message": "Create linter.yaml",
                        "timestamp": "2020-01-22T19:33:05Z",
                        "author": {
                            "name": "Octo Cat",
                            "email": "octocat@github.com",
                        },
                        "committer": {
                            "name": "GitHub",
                            "email": "noreply@github.com",
                        },
                    },
                    "repository": {
                        "id": 1296269,
                        "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                        "name": "Hello-World",
                        "full_name": "octocat/Hello-World",
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "private": False,
                        "html_url": "https://github.com/octocat/Hello-World",
                        "description": "This your first repo!",
                        "fork": False,
                        "url": "https://api.github.com/repos/octocat/Hello-World",
                        "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                        "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                        "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                        "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                        "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                        "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                        "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                        "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                        "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                        "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                        "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                        "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                        "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                        "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                        "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                        "git_url": "git:github.com/octocat/Hello-World.git",
                        "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                        "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                        "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                        "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                        "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                        "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                        "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                        "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                        "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                        "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                        "ssh_url": "git@github.com:octocat/Hello-World.git",
                        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                        "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                        "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                        "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                        "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                        "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                        "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks",
                    },
                    "head_repository": {
                        "id": 217723378,
                        "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
                        "name": "octo-repo",
                        "full_name": "octo-org/octo-repo",
                        "private": True,
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "html_url": "https://github.com/octo-org/octo-repo",
                        "description": None,
                        "fork": False,
                        "url": "https://api.github.com/repos/octo-org/octo-repo",
                        "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
                        "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
                        "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
                        "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
                        "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
                        "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
                        "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
                        "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
                        "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
                        "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
                        "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
                        "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
                        "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
                        "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
                        "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
                        "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
                        "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
                        "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
                        "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
                        "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
                        "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
                        "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
                        "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
                        "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
                        "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
                        "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
                        "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
                        "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
                        "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
                        "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
                        "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
                        "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
                        "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
                    },
                },
                {
                    "id": 3,
                    "name": "Build",
                    "node_id": "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==",
                    "check_suite_id": 42,
                    "check_suite_node_id": "MDEwOkNoZWNrU3VpdGU0Mg==",
                    "head_branch": "master",
                    "head_sha": "acb5820ced9479c074f688cc328bf03f341a511d",
                    "run_number": 562,
                    "event": "push",
                    "status": "queued",
                    "conclusion": None,
                    "workflow_id": 159038,
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
                    "html_url": "https://github.com/octo-org/octo-repo/actions/runs/30433642",
                    "pull_requests": [],
                    "created_at": "2020-01-22T19:33:08Z",
                    "updated_at": "2020-01-22T19:33:08Z",
                    "actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "run_attempt": 1,
                    "run_started_at": "2020-01-22T19:33:08Z",
                    "triggering_actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
                    "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
                    "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
                    "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
                    "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
                    "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
                    "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
                    "head_commit": {
                        "id": "acb5820ced9479c074f688cc328bf03f341a511d",
                        "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
                        "message": "Create linter.yaml",
                        "timestamp": "2020-01-22T19:33:05Z",
                        "author": {
                            "name": "Octo Cat",
                            "email": "octocat@github.com",
                        },
                        "committer": {
                            "name": "GitHub",
                            "email": "noreply@github.com",
                        },
                    },
                    "repository": {
                        "id": 1296269,
                        "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                        "name": "Hello-World",
                        "full_name": "octocat/Hello-World",
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "private": False,
                        "html_url": "https://github.com/octocat/Hello-World",
                        "description": "This your first repo!",
                        "fork": False,
                        "url": "https://api.github.com/repos/octocat/Hello-World",
                        "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                        "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                        "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                        "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                        "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                        "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                        "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                        "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                        "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                        "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                        "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                        "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                        "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                        "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                        "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                        "git_url": "git:github.com/octocat/Hello-World.git",
                        "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                        "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                        "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                        "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                        "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                        "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                        "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                        "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                        "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                        "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                        "ssh_url": "git@github.com:octocat/Hello-World.git",
                        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                        "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                        "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                        "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                        "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                        "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                        "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks",
                    },
                    "head_repository": {
                        "id": 217723378,
                        "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
                        "name": "octo-repo",
                        "full_name": "octo-org/octo-repo",
                        "private": True,
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "html_url": "https://github.com/octo-org/octo-repo",
                        "description": None,
                        "fork": False,
                        "url": "https://api.github.com/repos/octo-org/octo-repo",
                        "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
                        "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
                        "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
                        "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
                        "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
                        "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
                        "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
                        "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
                        "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
                        "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
                        "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
                        "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
                        "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
                        "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
                        "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
                        "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
                        "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
                        "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
                        "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
                        "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
                        "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
                        "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
                        "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
                        "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
                        "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
                        "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
                        "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
                        "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
                        "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
                        "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
                        "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
                        "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
                        "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
                    },
                },
            ]
        }

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(
            self.api.get_workflow_runs(
                "foo/bar",
                actor="foo",
                branch="stable",
                exclude_pull_requests=True,
            )
        )
        run = await anext(async_it)
        self.assertEqual(run.id, 1)
        run = await anext(async_it)
        self.assertEqual(run.id, 2)
        run = await anext(async_it)
        self.assertEqual(run.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/actions/runs",
            params={
                "actor": "foo",
                "branch": "stable",
                "exclude_pull_requests": True,
                "per_page": "100",
            },
        )

    async def test_get_workflow_runs_for_workflow(self):
        response1 = create_response()
        response1.json.return_value = {
            "workflow_runs": [
                {
                    "id": 1,
                    "name": "Build",
                    "node_id": "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==",
                    "check_suite_id": 42,
                    "check_suite_node_id": "MDEwOkNoZWNrU3VpdGU0Mg==",
                    "head_branch": "master",
                    "head_sha": "acb5820ced9479c074f688cc328bf03f341a511d",
                    "run_number": 562,
                    "event": "push",
                    "status": "queued",
                    "conclusion": None,
                    "workflow_id": 159038,
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
                    "html_url": "https://github.com/octo-org/octo-repo/actions/runs/30433642",
                    "pull_requests": [],
                    "created_at": "2020-01-22T19:33:08Z",
                    "updated_at": "2020-01-22T19:33:08Z",
                    "actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "run_attempt": 1,
                    "run_started_at": "2020-01-22T19:33:08Z",
                    "triggering_actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
                    "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
                    "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
                    "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
                    "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
                    "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
                    "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
                    "head_commit": {
                        "id": "acb5820ced9479c074f688cc328bf03f341a511d",
                        "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
                        "message": "Create linter.yaml",
                        "timestamp": "2020-01-22T19:33:05Z",
                        "author": {
                            "name": "Octo Cat",
                            "email": "octocat@github.com",
                        },
                        "committer": {
                            "name": "GitHub",
                            "email": "noreply@github.com",
                        },
                    },
                    "repository": {
                        "id": 1296269,
                        "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                        "name": "Hello-World",
                        "full_name": "octocat/Hello-World",
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "private": False,
                        "html_url": "https://github.com/octocat/Hello-World",
                        "description": "This your first repo!",
                        "fork": False,
                        "url": "https://api.github.com/repos/octocat/Hello-World",
                        "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                        "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                        "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                        "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                        "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                        "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                        "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                        "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                        "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                        "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                        "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                        "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                        "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                        "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                        "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                        "git_url": "git:github.com/octocat/Hello-World.git",
                        "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                        "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                        "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                        "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                        "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                        "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                        "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                        "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                        "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                        "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                        "ssh_url": "git@github.com:octocat/Hello-World.git",
                        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                        "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                        "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                        "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                        "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                        "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                        "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks",
                    },
                    "head_repository": {
                        "id": 217723378,
                        "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
                        "name": "octo-repo",
                        "full_name": "octo-org/octo-repo",
                        "private": True,
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "html_url": "https://github.com/octo-org/octo-repo",
                        "description": None,
                        "fork": False,
                        "url": "https://api.github.com/repos/octo-org/octo-repo",
                        "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
                        "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
                        "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
                        "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
                        "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
                        "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
                        "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
                        "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
                        "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
                        "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
                        "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
                        "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
                        "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
                        "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
                        "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
                        "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
                        "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
                        "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
                        "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
                        "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
                        "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
                        "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
                        "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
                        "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
                        "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
                        "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
                        "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
                        "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
                        "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
                        "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
                        "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
                        "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
                        "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
                    },
                }
            ]
        }
        response2 = create_response()
        response2.json.return_value = {
            "workflow_runs": [
                {
                    "id": 2,
                    "name": "Build",
                    "node_id": "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==",
                    "check_suite_id": 42,
                    "check_suite_node_id": "MDEwOkNoZWNrU3VpdGU0Mg==",
                    "head_branch": "master",
                    "head_sha": "acb5820ced9479c074f688cc328bf03f341a511d",
                    "run_number": 562,
                    "event": "push",
                    "status": "queued",
                    "conclusion": None,
                    "workflow_id": 159038,
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
                    "html_url": "https://github.com/octo-org/octo-repo/actions/runs/30433642",
                    "pull_requests": [],
                    "created_at": "2020-01-22T19:33:08Z",
                    "updated_at": "2020-01-22T19:33:08Z",
                    "actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "run_attempt": 1,
                    "run_started_at": "2020-01-22T19:33:08Z",
                    "triggering_actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
                    "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
                    "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
                    "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
                    "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
                    "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
                    "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
                    "head_commit": {
                        "id": "acb5820ced9479c074f688cc328bf03f341a511d",
                        "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
                        "message": "Create linter.yaml",
                        "timestamp": "2020-01-22T19:33:05Z",
                        "author": {
                            "name": "Octo Cat",
                            "email": "octocat@github.com",
                        },
                        "committer": {
                            "name": "GitHub",
                            "email": "noreply@github.com",
                        },
                    },
                    "repository": {
                        "id": 1296269,
                        "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                        "name": "Hello-World",
                        "full_name": "octocat/Hello-World",
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "private": False,
                        "html_url": "https://github.com/octocat/Hello-World",
                        "description": "This your first repo!",
                        "fork": False,
                        "url": "https://api.github.com/repos/octocat/Hello-World",
                        "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                        "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                        "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                        "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                        "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                        "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                        "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                        "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                        "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                        "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                        "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                        "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                        "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                        "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                        "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                        "git_url": "git:github.com/octocat/Hello-World.git",
                        "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                        "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                        "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                        "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                        "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                        "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                        "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                        "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                        "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                        "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                        "ssh_url": "git@github.com:octocat/Hello-World.git",
                        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                        "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                        "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                        "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                        "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                        "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                        "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks",
                    },
                    "head_repository": {
                        "id": 217723378,
                        "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
                        "name": "octo-repo",
                        "full_name": "octo-org/octo-repo",
                        "private": True,
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "html_url": "https://github.com/octo-org/octo-repo",
                        "description": None,
                        "fork": False,
                        "url": "https://api.github.com/repos/octo-org/octo-repo",
                        "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
                        "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
                        "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
                        "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
                        "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
                        "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
                        "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
                        "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
                        "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
                        "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
                        "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
                        "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
                        "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
                        "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
                        "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
                        "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
                        "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
                        "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
                        "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
                        "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
                        "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
                        "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
                        "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
                        "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
                        "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
                        "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
                        "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
                        "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
                        "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
                        "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
                        "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
                        "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
                        "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
                    },
                },
                {
                    "id": 3,
                    "name": "Build",
                    "node_id": "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==",
                    "check_suite_id": 42,
                    "check_suite_node_id": "MDEwOkNoZWNrU3VpdGU0Mg==",
                    "head_branch": "master",
                    "head_sha": "acb5820ced9479c074f688cc328bf03f341a511d",
                    "run_number": 562,
                    "event": "push",
                    "status": "queued",
                    "conclusion": None,
                    "workflow_id": 159038,
                    "url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
                    "html_url": "https://github.com/octo-org/octo-repo/actions/runs/30433642",
                    "pull_requests": [],
                    "created_at": "2020-01-22T19:33:08Z",
                    "updated_at": "2020-01-22T19:33:08Z",
                    "actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "run_attempt": 1,
                    "run_started_at": "2020-01-22T19:33:08Z",
                    "triggering_actor": {
                        "login": "octocat",
                        "id": 1,
                        "node_id": "MDQ6VXNlcjE=",
                        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/octocat",
                        "html_url": "https://github.com/octocat",
                        "followers_url": "https://api.github.com/users/octocat/followers",
                        "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                        "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                        "organizations_url": "https://api.github.com/users/octocat/orgs",
                        "repos_url": "https://api.github.com/users/octocat/repos",
                        "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/octocat/received_events",
                        "type": "User",
                        "site_admin": False,
                    },
                    "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
                    "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
                    "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
                    "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
                    "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
                    "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
                    "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
                    "head_commit": {
                        "id": "acb5820ced9479c074f688cc328bf03f341a511d",
                        "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
                        "message": "Create linter.yaml",
                        "timestamp": "2020-01-22T19:33:05Z",
                        "author": {
                            "name": "Octo Cat",
                            "email": "octocat@github.com",
                        },
                        "committer": {
                            "name": "GitHub",
                            "email": "noreply@github.com",
                        },
                    },
                    "repository": {
                        "id": 1296269,
                        "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                        "name": "Hello-World",
                        "full_name": "octocat/Hello-World",
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "private": False,
                        "html_url": "https://github.com/octocat/Hello-World",
                        "description": "This your first repo!",
                        "fork": False,
                        "url": "https://api.github.com/repos/octocat/Hello-World",
                        "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                        "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                        "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                        "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                        "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                        "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                        "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                        "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                        "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                        "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                        "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                        "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                        "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                        "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                        "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                        "git_url": "git:github.com/octocat/Hello-World.git",
                        "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                        "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                        "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                        "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                        "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                        "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                        "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                        "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                        "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                        "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                        "ssh_url": "git@github.com:octocat/Hello-World.git",
                        "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                        "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                        "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                        "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                        "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                        "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                        "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                        "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks",
                    },
                    "head_repository": {
                        "id": 217723378,
                        "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
                        "name": "octo-repo",
                        "full_name": "octo-org/octo-repo",
                        "private": True,
                        "owner": {
                            "login": "octocat",
                            "id": 1,
                            "node_id": "MDQ6VXNlcjE=",
                            "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                            "gravatar_id": "",
                            "url": "https://api.github.com/users/octocat",
                            "html_url": "https://github.com/octocat",
                            "followers_url": "https://api.github.com/users/octocat/followers",
                            "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                            "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                            "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                            "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                            "organizations_url": "https://api.github.com/users/octocat/orgs",
                            "repos_url": "https://api.github.com/users/octocat/repos",
                            "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                            "received_events_url": "https://api.github.com/users/octocat/received_events",
                            "type": "User",
                            "site_admin": False,
                        },
                        "html_url": "https://github.com/octo-org/octo-repo",
                        "description": None,
                        "fork": False,
                        "url": "https://api.github.com/repos/octo-org/octo-repo",
                        "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
                        "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
                        "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
                        "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
                        "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
                        "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
                        "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
                        "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
                        "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
                        "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
                        "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
                        "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
                        "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
                        "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
                        "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
                        "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
                        "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
                        "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
                        "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
                        "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
                        "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
                        "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
                        "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
                        "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
                        "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
                        "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
                        "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
                        "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
                        "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
                        "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
                        "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
                        "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
                        "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
                        "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
                        "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
                        "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
                    },
                },
            ]
        }

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(
            self.api.get_workflow_runs(
                "foo/bar",
                "ci.yml",
                actor="foo",
                branch="stable",
                exclude_pull_requests=True,
            )
        )
        run = await anext(async_it)
        self.assertEqual(run.id, 1)
        run = await anext(async_it)
        self.assertEqual(run.id, 2)
        run = await anext(async_it)
        self.assertEqual(run.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml/runs",
            params={
                "actor": "foo",
                "branch": "stable",
                "exclude_pull_requests": True,
                "per_page": "100",
            },
        )

    async def test_get_workflow_run(self):
        response = create_response()
        response.json.return_value = {
            "id": 1,
            "name": "Build",
            "node_id": "MDEyOldvcmtmbG93IFJ1bjI2OTI4OQ==",
            "check_suite_id": 42,
            "check_suite_node_id": "MDEwOkNoZWNrU3VpdGU0Mg==",
            "head_branch": "master",
            "head_sha": "acb5820ced9479c074f688cc328bf03f341a511d",
            "run_number": 562,
            "event": "push",
            "status": "queued",
            "conclusion": None,
            "workflow_id": 159038,
            "url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642",
            "html_url": "https://github.com/octo-org/octo-repo/actions/runs/30433642",
            "pull_requests": [],
            "created_at": "2020-01-22T19:33:08Z",
            "updated_at": "2020-01-22T19:33:08Z",
            "actor": {
                "login": "octocat",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": False,
            },
            "run_attempt": 1,
            "run_started_at": "2020-01-22T19:33:08Z",
            "triggering_actor": {
                "login": "octocat",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/octocat",
                "html_url": "https://github.com/octocat",
                "followers_url": "https://api.github.com/users/octocat/followers",
                "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                "organizations_url": "https://api.github.com/users/octocat/orgs",
                "repos_url": "https://api.github.com/users/octocat/repos",
                "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                "received_events_url": "https://api.github.com/users/octocat/received_events",
                "type": "User",
                "site_admin": False,
            },
            "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
            "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
            "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
            "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
            "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
            "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
            "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
            "head_commit": {
                "id": "acb5820ced9479c074f688cc328bf03f341a511d",
                "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
                "message": "Create linter.yaml",
                "timestamp": "2020-01-22T19:33:05Z",
                "author": {
                    "name": "Octo Cat",
                    "email": "octocat@github.com",
                },
                "committer": {
                    "name": "GitHub",
                    "email": "noreply@github.com",
                },
            },
            "repository": {
                "id": 1296269,
                "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
                "name": "Hello-World",
                "full_name": "octocat/Hello-World",
                "owner": {
                    "login": "octocat",
                    "id": 1,
                    "node_id": "MDQ6VXNlcjE=",
                    "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/octocat",
                    "html_url": "https://github.com/octocat",
                    "followers_url": "https://api.github.com/users/octocat/followers",
                    "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                    "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                    "organizations_url": "https://api.github.com/users/octocat/orgs",
                    "repos_url": "https://api.github.com/users/octocat/repos",
                    "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/octocat/received_events",
                    "type": "User",
                    "site_admin": False,
                },
                "private": False,
                "html_url": "https://github.com/octocat/Hello-World",
                "description": "This your first repo!",
                "fork": False,
                "url": "https://api.github.com/repos/octocat/Hello-World",
                "archive_url": "https://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}",
                "assignees_url": "https://api.github.com/repos/octocat/Hello-World/assignees{/user}",
                "blobs_url": "https://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}",
                "branches_url": "https://api.github.com/repos/octocat/Hello-World/branches{/branch}",
                "collaborators_url": "https://api.github.com/repos/octocat/Hello-World/collaborators{/collaborator}",
                "comments_url": "https://api.github.com/repos/octocat/Hello-World/comments{/number}",
                "commits_url": "https://api.github.com/repos/octocat/Hello-World/commits{/sha}",
                "compare_url": "https://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}",
                "contents_url": "https://api.github.com/repos/octocat/Hello-World/contents/{+path}",
                "contributors_url": "https://api.github.com/repos/octocat/Hello-World/contributors",
                "deployments_url": "https://api.github.com/repos/octocat/Hello-World/deployments",
                "downloads_url": "https://api.github.com/repos/octocat/Hello-World/downloads",
                "events_url": "https://api.github.com/repos/octocat/Hello-World/events",
                "forks_url": "https://api.github.com/repos/octocat/Hello-World/forks",
                "git_commits_url": "https://api.github.com/repos/octocat/Hello-World/git/commits{/sha}",
                "git_refs_url": "https://api.github.com/repos/octocat/Hello-World/git/refs{/sha}",
                "git_tags_url": "https://api.github.com/repos/octocat/Hello-World/git/tags{/sha}",
                "git_url": "git:github.com/octocat/Hello-World.git",
                "issue_comment_url": "https://api.github.com/repos/octocat/Hello-World/issues/comments{/number}",
                "issue_events_url": "https://api.github.com/repos/octocat/Hello-World/issues/events{/number}",
                "issues_url": "https://api.github.com/repos/octocat/Hello-World/issues{/number}",
                "keys_url": "https://api.github.com/repos/octocat/Hello-World/keys{/key_id}",
                "labels_url": "https://api.github.com/repos/octocat/Hello-World/labels{/name}",
                "languages_url": "https://api.github.com/repos/octocat/Hello-World/languages",
                "merges_url": "https://api.github.com/repos/octocat/Hello-World/merges",
                "milestones_url": "https://api.github.com/repos/octocat/Hello-World/milestones{/number}",
                "notifications_url": "https://api.github.com/repos/octocat/Hello-World/notifications{?since,all,participating}",
                "pulls_url": "https://api.github.com/repos/octocat/Hello-World/pulls{/number}",
                "releases_url": "https://api.github.com/repos/octocat/Hello-World/releases{/id}",
                "ssh_url": "git@github.com:octocat/Hello-World.git",
                "stargazers_url": "https://api.github.com/repos/octocat/Hello-World/stargazers",
                "statuses_url": "https://api.github.com/repos/octocat/Hello-World/statuses/{sha}",
                "subscribers_url": "https://api.github.com/repos/octocat/Hello-World/subscribers",
                "subscription_url": "https://api.github.com/repos/octocat/Hello-World/subscription",
                "tags_url": "https://api.github.com/repos/octocat/Hello-World/tags",
                "teams_url": "https://api.github.com/repos/octocat/Hello-World/teams",
                "trees_url": "https://api.github.com/repos/octocat/Hello-World/git/trees{/sha}",
                "hooks_url": "http://api.github.com/repos/octocat/Hello-World/hooks",
            },
            "head_repository": {
                "id": 217723378,
                "node_id": "MDEwOlJlcG9zaXRvcnkyMTc3MjMzNzg=",
                "name": "octo-repo",
                "full_name": "octo-org/octo-repo",
                "private": True,
                "owner": {
                    "login": "octocat",
                    "id": 1,
                    "node_id": "MDQ6VXNlcjE=",
                    "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/octocat",
                    "html_url": "https://github.com/octocat",
                    "followers_url": "https://api.github.com/users/octocat/followers",
                    "following_url": "https://api.github.com/users/octocat/following{/other_user}",
                    "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
                    "organizations_url": "https://api.github.com/users/octocat/orgs",
                    "repos_url": "https://api.github.com/users/octocat/repos",
                    "events_url": "https://api.github.com/users/octocat/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/octocat/received_events",
                    "type": "User",
                    "site_admin": False,
                },
                "html_url": "https://github.com/octo-org/octo-repo",
                "description": None,
                "fork": False,
                "url": "https://api.github.com/repos/octo-org/octo-repo",
                "forks_url": "https://api.github.com/repos/octo-org/octo-repo/forks",
                "keys_url": "https://api.github.com/repos/octo-org/octo-repo/keys{/key_id}",
                "collaborators_url": "https://api.github.com/repos/octo-org/octo-repo/collaborators{/collaborator}",
                "teams_url": "https://api.github.com/repos/octo-org/octo-repo/teams",
                "hooks_url": "https://api.github.com/repos/octo-org/octo-repo/hooks",
                "issue_events_url": "https://api.github.com/repos/octo-org/octo-repo/issues/events{/number}",
                "events_url": "https://api.github.com/repos/octo-org/octo-repo/events",
                "assignees_url": "https://api.github.com/repos/octo-org/octo-repo/assignees{/user}",
                "branches_url": "https://api.github.com/repos/octo-org/octo-repo/branches{/branch}",
                "tags_url": "https://api.github.com/repos/octo-org/octo-repo/tags",
                "blobs_url": "https://api.github.com/repos/octo-org/octo-repo/git/blobs{/sha}",
                "git_tags_url": "https://api.github.com/repos/octo-org/octo-repo/git/tags{/sha}",
                "git_refs_url": "https://api.github.com/repos/octo-org/octo-repo/git/refs{/sha}",
                "trees_url": "https://api.github.com/repos/octo-org/octo-repo/git/trees{/sha}",
                "statuses_url": "https://api.github.com/repos/octo-org/octo-repo/statuses/{sha}",
                "languages_url": "https://api.github.com/repos/octo-org/octo-repo/languages",
                "stargazers_url": "https://api.github.com/repos/octo-org/octo-repo/stargazers",
                "contributors_url": "https://api.github.com/repos/octo-org/octo-repo/contributors",
                "subscribers_url": "https://api.github.com/repos/octo-org/octo-repo/subscribers",
                "subscription_url": "https://api.github.com/repos/octo-org/octo-repo/subscription",
                "commits_url": "https://api.github.com/repos/octo-org/octo-repo/commits{/sha}",
                "git_commits_url": "https://api.github.com/repos/octo-org/octo-repo/git/commits{/sha}",
                "comments_url": "https://api.github.com/repos/octo-org/octo-repo/comments{/number}",
                "issue_comment_url": "https://api.github.com/repos/octo-org/octo-repo/issues/comments{/number}",
                "contents_url": "https://api.github.com/repos/octo-org/octo-repo/contents/{+path}",
                "compare_url": "https://api.github.com/repos/octo-org/octo-repo/compare/{base}...{head}",
                "merges_url": "https://api.github.com/repos/octo-org/octo-repo/merges",
                "archive_url": "https://api.github.com/repos/octo-org/octo-repo/{archive_format}{/ref}",
                "downloads_url": "https://api.github.com/repos/octo-org/octo-repo/downloads",
                "issues_url": "https://api.github.com/repos/octo-org/octo-repo/issues{/number}",
                "pulls_url": "https://api.github.com/repos/octo-org/octo-repo/pulls{/number}",
                "milestones_url": "https://api.github.com/repos/octo-org/octo-repo/milestones{/number}",
                "notifications_url": "https://api.github.com/repos/octo-org/octo-repo/notifications{?since,all,participating}",
                "labels_url": "https://api.github.com/repos/octo-org/octo-repo/labels{/name}",
                "releases_url": "https://api.github.com/repos/octo-org/octo-repo/releases{/id}",
                "deployments_url": "https://api.github.com/repos/octo-org/octo-repo/deployments",
            },
        }
        self.client.get.return_value = response

        workflow = await self.api.get_workflow_run("foo/bar", "123")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/runs/123"
        )

        self.assertEqual(workflow.id, 1)

    async def test_get_workflow_run_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get_workflow_run("foo/bar", "123")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/runs/123"
        )

    async def test_create_workflow_dispatch(self):
        response = create_response()
        self.client.post.return_value = response

        input_dict = {"foo": "bar"}

        await self.api.create_workflow_dispatch(
            "foo/bar", "ci.yml", ref="stable", inputs=input_dict
        )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml/dispatches",
            data={"ref": "stable", "inputs": input_dict},
        )

    async def test_create_workflow_dispatch_failure(self):
        response = create_response()
        self.client.post.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        input_dict = {"foo": "bar"}

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.create_workflow_dispatch(
                "foo/bar", "ci.yml", ref="stable", inputs=input_dict
            )

        self.client.post.assert_awaited_once_with(
            "/repos/foo/bar/actions/workflows/ci.yml/dispatches",
            data={"ref": "stable", "inputs": input_dict},
        )


class GitHubWorkflowsTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflows(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflows": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflows("foo/bar")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflows_with_pagination(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "workflows": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "workflows": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(100, 120)
                ],
            },
        ]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflows("foo/bar")

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows",
            params={"per_page": 100, "page": 1},
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows",
            params={"per_page": 100, "page": 2},
        )
        requests_mock.assert_has_calls(
            [
                call.__bool__(),
                call(*args1, **kwargs1),
                call().raise_for_status(),
                call().json(),
                call.__bool__(),
                call(*args2, **kwargs2),
                call().raise_for_status(),
                call().json(),
            ]
        )

        self.assertEqual(len(artifacts), 120)
        self.assertEqual(artifacts[0]["name"], "Foo-0")
        self.assertEqual(artifacts[119]["name"], "Foo-119")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Testing Status Message", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_workflow("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_create_workflow_dispatch(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.create_workflow_dispatch("foo/bar", "123", ref="main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/123"
            "/dispatches",
            json={"ref": "main"},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.post")
    def test_create_workflow_dispatch_failure(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Dispatch Failed", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.create_workflow_dispatch("foo/bar", "123", ref="main")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/123"
            "/dispatches",
            json={"ref": "main"},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_runs(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs("foo/bar")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_runs_with_pagination(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "workflow_runs": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "workflow_runs": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(100, 120)
                ],
            },
        ]
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs("foo/bar")

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs",
            params={"per_page": 100, "page": 1},
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs",
            params={"per_page": 100, "page": 2},
        )
        requests_mock.assert_has_calls(
            [
                call.__bool__(),
                call(*args1, **kwargs1),
                call().raise_for_status(),
                call().json(),
                call.__bool__(),
                call(*args2, **kwargs2),
                call().raise_for_status(),
                call().json(),
            ]
        )

        self.assertEqual(len(artifacts), 120)
        self.assertEqual(artifacts[0]["name"], "Foo-0")
        self.assertEqual(artifacts[119]["name"], "Foo-119")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_runs_with_params(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs(
            "foo/bar",
            actor="Foo",
            branch="main",
            event="workflow_dispatch",
            status="completed",
            created=">=2022-09-01",
            exclude_pull_requests=True,
        )

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs",
            params={
                "per_page": 100,
                "page": 1,
                "actor": "Foo",
                "branch": "main",
                "event": "workflow_dispatch",
                "status": "completed",
                "created": ">=2022-09-01",
                "exclude_pull_requests": True,
            },
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_runs_for_workflow(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [
                {
                    "id": 11,
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_runs("foo/bar", "foo")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/workflows/foo/runs",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_run(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_run("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_run_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Workflow Run Not Found", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_workflow_run("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
