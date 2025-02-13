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

# pylint: disable=redefined-builtin, line-too-long

import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import httpx

from pontos.github.api import GitHubRESTApi
from pontos.github.api.artifacts import GitHubAsyncRESTArtifacts
from pontos.helper import DEFAULT_TIMEOUT
from tests import AsyncIteratorMock, AsyncMock, aiter, anext
from tests.github.api import (
    GitHubAsyncRESTTestCase,
    create_response,
    default_request,
)

here = Path(__file__).parent


class GitHubAsyncRESTArtifactsTestCase(GitHubAsyncRESTTestCase):
    api_cls = GitHubAsyncRESTArtifacts

    async def test_get(self):
        response = create_response()
        response.json.return_value = {
            "id": 1,
            "node_id": "MDg6QXJ0aWZhY3QxMQ==",
            "name": "Rails",
            "size_in_bytes": 556,
            "url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/11",
            "archive_download_url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/11/zip",
            "expired": False,
            "created_at": "2020-01-10T14:59:22Z",
            "expires_at": "2020-03-21T14:59:22Z",
            "updated_at": "2020-02-21T14:59:22Z",
            "workflow_run": {
                "id": 2332938,
                "repository_id": 1296269,
                "head_repository_id": 1296269,
                "head_branch": "main",
                "head_sha": "328faa0536e6fef19753d9d91dc96a9931694ce3",
            },
        }
        self.client.get.return_value = response

        artifact = await self.api.get("foo/bar", "123")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/artifacts/123"
        )

        self.assertEqual(artifact.id, 1)

    async def test_get_failure(self):
        response = create_response()
        self.client.get.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.get("foo/bar", "123")

        self.client.get.assert_awaited_once_with(
            "/repos/foo/bar/actions/artifacts/123"
        )

    async def test_get_all(self):
        response1 = create_response()
        response1.json.return_value = {
            "artifacts": [
                {
                    "id": 1,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Rails",
                    "size_in_bytes": 556,
                    "url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/11",
                    "archive_download_url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/11/zip",
                    "expired": False,
                    "created_at": "2020-01-10T14:59:22Z",
                    "expires_at": "2020-03-21T14:59:22Z",
                    "updated_at": "2020-02-21T14:59:22Z",
                    "workflow_run": {
                        "id": 2332938,
                        "repository_id": 1296269,
                        "head_repository_id": 1296269,
                        "head_branch": "main",
                        "head_sha": "328faa0536e6fef19753d9d91dc96a9931694ce3",
                    },
                }
            ]
        }
        response2 = create_response()
        response2.json.return_value = {
            "artifacts": [
                {
                    "id": 2,
                    "node_id": "MDg6QXJ0aWZhY3QxMw==",
                    "name": "Test output",
                    "size_in_bytes": 453,
                    "url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/2",
                    "archive_download_url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/2/zip",
                    "expired": False,
                    "created_at": "2020-01-10T14:59:22Z",
                    "expires_at": "2020-03-21T14:59:22Z",
                    "updated_at": "2020-02-21T14:59:22Z",
                    "workflow_run": {
                        "id": 2332942,
                        "repository_id": 1296269,
                        "head_repository_id": 1296269,
                        "head_branch": "main",
                        "head_sha": "178f4f6090b3fccad4a65b3e83d076a622d59652",
                    },
                },
                {
                    "id": 3,
                    "node_id": "MDg6QXJ0aWZhY3QxMw==",
                    "name": "Test output",
                    "size_in_bytes": 123,
                    "url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/3",
                    "archive_download_url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/3/zip",
                    "expired": False,
                    "created_at": "2020-01-10T14:59:22Z",
                    "expires_at": "2020-03-21T14:59:22Z",
                    "updated_at": "2020-02-21T14:59:22Z",
                    "workflow_run": {
                        "id": 2332942,
                        "repository_id": 1296269,
                        "head_repository_id": 1296269,
                        "head_branch": "main",
                        "head_sha": "178f4f6090b3fccad4a65b3e83d076a622d59652",
                    },
                },
            ]
        }

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.get_all("foo/bar"))
        artifact = await anext(async_it)
        self.assertEqual(artifact.id, 1)
        artifact = await anext(async_it)
        self.assertEqual(artifact.id, 2)
        artifact = await anext(async_it)
        self.assertEqual(artifact.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/actions/artifacts",
            params={"per_page": "100"},
        )

    async def test_get_workflow_run_artifacts(self):
        response1 = create_response()
        response1.json.return_value = {
            "artifacts": [
                {
                    "id": 1,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Rails",
                    "size_in_bytes": 556,
                    "url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/1",
                    "archive_download_url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/1/zip",
                    "expired": False,
                    "created_at": "2020-01-10T14:59:22Z",
                    "expires_at": "2020-03-21T14:59:22Z",
                    "updated_at": "2020-02-21T14:59:22Z",
                    "workflow_run": {
                        "id": 2332938,
                        "repository_id": 1296269,
                        "head_repository_id": 1296269,
                        "head_branch": "main",
                        "head_sha": "328faa0536e6fef19753d9d91dc96a9931694ce3",
                    },
                }
            ]
        }
        response2 = create_response()
        response2.json.return_value = {
            "artifacts": [
                {
                    "id": 2,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Rails",
                    "size_in_bytes": 556,
                    "url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/2",
                    "archive_download_url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/2/zip",
                    "expired": False,
                    "created_at": "2020-01-10T14:59:22Z",
                    "expires_at": "2020-03-21T14:59:22Z",
                    "updated_at": "2020-02-21T14:59:22Z",
                    "workflow_run": {
                        "id": 2332938,
                        "repository_id": 1296269,
                        "head_repository_id": 1296269,
                        "head_branch": "main",
                        "head_sha": "328faa0536e6fef19753d9d91dc96a9931694ce3",
                    },
                },
                {
                    "id": 3,
                    "node_id": "MDg6QXJ0aWZhY3QxMw==",
                    "name": "Test output",
                    "size_in_bytes": 453,
                    "url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/3",
                    "archive_download_url": "https://api.github.com/repos/octo-org/octo-docs/actions/artifacts/3/zip",
                    "expired": False,
                    "created_at": "2020-01-10T14:59:22Z",
                    "expires_at": "2020-03-21T14:59:22Z",
                    "updated_at": "2020-02-21T14:59:22Z",
                    "workflow_run": {
                        "id": 2332942,
                        "repository_id": 1296269,
                        "head_repository_id": 1296269,
                        "head_branch": "main",
                        "head_sha": "178f4f6090b3fccad4a65b3e83d076a622d59652",
                    },
                },
            ]
        }

        self.client.get_all.return_value = AsyncIteratorMock(
            [response1, response2]
        )

        async_it = aiter(self.api.get_workflow_run_artifacts("foo/bar", "123"))
        artifact = await anext(async_it)
        self.assertEqual(artifact.id, 1)
        artifact = await anext(async_it)
        self.assertEqual(artifact.id, 2)
        artifact = await anext(async_it)
        self.assertEqual(artifact.id, 3)

        with self.assertRaises(StopAsyncIteration):
            await anext(async_it)

        self.client.get_all.assert_called_once_with(
            "/repos/foo/bar/actions/runs/123/artifacts",
            params={"per_page": "100"},
        )

    async def test_delete(self):
        response = create_response()
        self.client.delete.return_value = response

        await self.api.delete("foo/bar", "123")

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/actions/artifacts/123"
        )

    async def test_delete_failure(self):
        response = create_response()
        self.client.delete.side_effect = httpx.HTTPStatusError(
            "404", request=MagicMock(), response=response
        )

        with self.assertRaises(httpx.HTTPStatusError):
            await self.api.delete("foo/bar", "123")

        self.client.delete.assert_awaited_once_with(
            "/repos/foo/bar/actions/artifacts/123"
        )

    async def test_download(self):
        response = create_response(headers=MagicMock())
        response.headers.get.return_value = 2
        response.aiter_bytes.return_value = AsyncIteratorMock(["1", "2"])
        stream_context = AsyncMock()
        stream_context.__aenter__.return_value = response
        self.client.stream.return_value = stream_context

        async with self.api.download("foo/bar", 123) as download_iterable:
            it = aiter(download_iterable)
            content, progress = await anext(it)

            self.assertEqual(content, "1")
            self.assertEqual(progress, 50)

            content, progress = await anext(it)
            self.assertEqual(content, "2")
            self.assertEqual(progress, 100)

        self.client.stream.assert_called_once_with(
            "/repos/foo/bar/actions/artifacts/123/zip"
        )


class GitHubArtifactsTestCase(unittest.TestCase):
    @patch("pontos.github.api.api.httpx.get")
    def test_get_repository_artifacts(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "artifacts": [
                {
                    "id": 11,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_repository_artifacts("foo/bar")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_repository_artifacts_with_pagination(
        self, requests_mock: MagicMock
    ):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "artifacts": [
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
        artifacts = api.get_repository_artifacts("foo/bar")

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts",
            params={"per_page": 100, "page": 1},
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts",
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
    def test_get_repository_artifact(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.json.return_value = {
            "id": 123,
            "name": "Foo",
        }

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_repository_artifact("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(artifacts["id"], 123)
        self.assertEqual(artifacts["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_repository_artifact_invalid(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Testing Status Message", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.get_repository_artifact("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.helper.Path")
    @patch("pontos.github.api.api.httpx.stream")
    def test_download_repository_artifact(
        self, requests_mock: MagicMock, path_mock: MagicMock
    ):
        response = MagicMock()
        response.iter_bytes.return_value = [b"foo", b"bar", b"baz"]
        response_headers = MagicMock()
        response.headers = response_headers
        response_headers.get.return_value = None
        response_stream = MagicMock()
        response_stream.__enter__.return_value = response
        requests_mock.return_value = response_stream

        api = GitHubRESTApi("12345")
        download_file = path_mock()
        with api.download_repository_artifact(
            "foo/bar", "123", download_file
        ) as download_progress:
            args, kwargs = default_request(
                "GET",
                "https://api.github.com/repos/foo/bar/actions/artifacts/123/zip",  # pylint: disable=line-too-long
                timeout=DEFAULT_TIMEOUT,
            )
            requests_mock.assert_called_once_with(*args, **kwargs)
            response_headers.get.assert_called_once_with("content-length")

            self.assertIsNone(download_progress.length)

            it = iter(download_progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)
            progress = next(it)
            self.assertIsNone(progress)

            with self.assertRaises(StopIteration):
                next(it)

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_run_artifacts(self, requests_mock: MagicMock):
        response = MagicMock()
        response.links = None
        response.json.return_value = {
            "total_count": 1,
            "artifacts": [
                {
                    "id": 11,
                    "node_id": "MDg6QXJ0aWZhY3QxMQ==",
                    "name": "Foo",
                }
            ],
        }
        requests_mock.return_value = response
        api = GitHubRESTApi("12345")
        artifacts = api.get_workflow_run_artifacts("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123/artifacts",
            params={"per_page": 100, "page": 1},
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["name"], "Foo")

    @patch("pontos.github.api.api.httpx.get")
    def test_get_workflow_run_artifacts_with_pagination(
        self, requests_mock: MagicMock
    ):
        response = MagicMock()
        response.links = None
        response.json.side_effect = [
            {
                "total_count": 120,
                "artifacts": [
                    {
                        "id": id,
                        "name": f"Foo-{id}",
                    }
                    for id in range(0, 100)
                ],
            },
            {
                "total_count": 120,
                "artifacts": [
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
        artifacts = api.get_workflow_run_artifacts("foo/bar", "123")

        args1, kwargs1 = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123/artifacts",
            params={"per_page": 100, "page": 1},
        )
        args2, kwargs2 = default_request(
            "https://api.github.com/repos/foo/bar/actions/runs/123/artifacts",
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

    @patch("pontos.github.api.api.httpx.delete")
    def test_delete_repository_artifact(self, requests_mock: MagicMock):
        api = GitHubRESTApi("12345")
        api.delete_repository_artifact("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)

    @patch("pontos.github.api.api.httpx.delete")
    def test_delete_repository_artifact_failure(self, requests_mock: MagicMock):
        response = MagicMock(autospec=httpx.Response)
        response.is_success = False
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Delete Failed", request=None, response=response
        )

        requests_mock.return_value = response
        api = GitHubRESTApi("12345")

        with self.assertRaises(httpx.HTTPStatusError):
            api.delete_repository_artifact("foo/bar", "123")

        args, kwargs = default_request(
            "https://api.github.com/repos/foo/bar/actions/artifacts/123",
        )
        requests_mock.assert_called_once_with(*args, **kwargs)
