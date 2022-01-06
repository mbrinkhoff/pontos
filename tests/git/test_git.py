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

import unittest

from pathlib import Path
from unittest.mock import patch

from pontos.git import Git


class GitTestCase(unittest.TestCase):
    @patch("pontos.git.git._exec_git")
    def test_clone(self, exec_git_mock):
        git = Git()
        git.clone("http://foo/foo.git", Path("/bar"))

        exec_git_mock.assert_called_once_with(
            "clone", "http://foo/foo.git", "/bar", cwd=None
        )

    @patch("pontos.git.git._exec_git")
    def test_clone_with_remote(self, exec_git_mock):
        git = Git()
        git.clone("http://foo/foo.git", Path("/bar"), remote="foo")

        exec_git_mock.assert_called_once_with(
            "clone", "-o", "foo", "http://foo/foo.git", "/bar", cwd=None
        )

    @patch("pontos.git.git._exec_git")
    def test_clone_with_branch(self, exec_git_mock):
        git = Git()
        git.clone("http://foo/foo.git", Path("/bar"), branch="foo")

        exec_git_mock.assert_called_once_with(
            "clone", "-b", "foo", "http://foo/foo.git", "/bar", cwd=None
        )

    @patch("pontos.git.git._exec_git")
    def test_clone_with_depth(self, exec_git_mock):
        git = Git()
        git.clone("http://foo/foo.git", Path("/bar"), depth=1)

        exec_git_mock.assert_called_once_with(
            "clone", "--depth", 1, "http://foo/foo.git", "/bar", cwd=None
        )

    @patch("pontos.git.git._exec_git")
    def test_init(self, exec_git_mock):
        git = Git()
        git.init()

        exec_git_mock.assert_called_once_with("init", cwd=None)

    @patch("pontos.git.git._exec_git")
    def test_init_bare(self, exec_git_mock):
        git = Git()
        git.init(bare=True)

        exec_git_mock.assert_called_once_with("init", "--bare", cwd=None)

    def test_cwd(self):
        git = Git()

        self.assertIsNone(git.cwd)

        new_cwd = Path("foo")
        git.cwd = new_cwd

        self.assertEqual(git.cwd, new_cwd.absolute())

    @patch("pontos.git.git._exec_git")
    def test_create_branch(self, exec_git_mock):
        git = Git()
        git.create_branch("foo")

        exec_git_mock.assert_called_once_with("checkout", "-b", "foo", cwd=None)

    @patch("pontos.git.git._exec_git")
    def test_create_branch_with_starting_point(self, exec_git_mock):
        git = Git()
        git.create_branch("foo", start_point="bar")

        exec_git_mock.assert_called_once_with(
            "checkout", "-b", "foo", "bar", cwd=None
        )

    @patch("pontos.git.git._exec_git")
    def test_rebase(self, exec_git_mock):
        git = Git()
        git.rebase("foo")

        exec_git_mock.assert_called_once_with("rebase", "foo", cwd=None)

    @patch("pontos.git.git._exec_git")
    def test_rebase_with_head(self, exec_git_mock):
        git = Git()
        git.rebase("foo", head="bar")

        exec_git_mock.assert_called_once_with("rebase", "foo", "bar", cwd=None)

    @patch("pontos.git.git._exec_git")
    def test_rebase_with_head_and_onto(self, exec_git_mock):
        git = Git()
        git.rebase("foo", head="bar", onto="staging")

        exec_git_mock.assert_called_once_with(
            "rebase", "--onto", "staging", "foo", "bar", cwd=None
        )

    @patch("pontos.git.git._exec_git")
    def test_push(self, exec_git_mock):
        git = Git()
        git.push()

        exec_git_mock.assert_called_once_with("push", cwd=None)

    @patch("pontos.git.git._exec_git")
    def test_push_with_remote(self, exec_git_mock):
        git = Git()
        git.push(remote="foo")

        exec_git_mock.assert_called_once_with("push", "foo", cwd=None)

    @patch("pontos.git.git._exec_git")
    def test_push_with_remote_and_branch(self, exec_git_mock):
        git = Git()
        git.push(remote="foo", branch="bar")

        exec_git_mock.assert_called_once_with("push", "foo", "bar", cwd=None)

    @patch("pontos.git.git._exec_git")
    def test_config(self, exec_git_mock):
        git = Git()
        git.config("foo", "bar")

        exec_git_mock.assert_called_once_with("config", "foo", "bar", cwd=None)

    @patch("pontos.git.git._exec_git")
    def test_cherry_pick(self, exec_git_mock):
        git = Git()
        git.cherry_pick("foo")

        exec_git_mock.assert_called_once_with("cherry-pick", "foo", cwd=None)
