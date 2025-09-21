import pytest

import os, tempfile
from pathlib import Path
import warnings

from hidos import util
from hidos import __main__


SNAPSHOT_CASE = Path(__file__).parent / "cases" / "snapshot"

CLEAN_SWHIDS = {
    'just_a_file.txt': 'swh:1:cnt:e7ee9eec323387d82a370674c1e2996d25c2414d',
    'smallest': 'swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f',
    'with_dir': 'swh:1:dir:3f58423dff95441bfc536f3214db58ce9a7a6e99',
}

WARN_SWHIDS = {
    'with_hidden_file': 'swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f',
    'with_hidden_dir': 'swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f',
    'with_exec_bit': 'swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f',
}


def test_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert "swh:1:dir:" + util.EMPTY_TREE == util.swhid_from_path(tmpdir)


def test_with_subdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, "empty_subdir_should_be_ignored"))
        assert "swh:1:dir:" + util.EMPTY_TREE == util.swhid_from_path(tmpdir)


@pytest.mark.parametrize("case", CLEAN_SWHIDS.keys())
def test_clean_swhids(case):
    with warnings.catch_warnings():
        # fail test if warning
        warnings.simplefilter("error")
        assert CLEAN_SWHIDS[case] == util.swhid_from_path(SNAPSHOT_CASE / case)


@pytest.mark.parametrize("case", WARN_SWHIDS.keys())
def test_warn_swhids(case):
    with pytest.warns(UserWarning):
        assert WARN_SWHIDS[case] == util.swhid_from_path(SNAPSHOT_CASE / case)


def test_with_symlink():
    with pytest.raises(ValueError):
        util.swhid_from_path(SNAPSHOT_CASE / "with_symlink")


def test_with_dir_symlink():
    with pytest.raises(ValueError):
        util.swhid_from_path(SNAPSHOT_CASE / "with_dir_symlink")


def test_cli_hash(capsys):
    src = SNAPSHOT_CASE / 'smallest'
    retcode = __main__.main(["hash", str(src)])
    assert retcode == 0
    got = capsys.readouterr().out.strip() 
    assert got == "swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f"


def get_swhid_from_git(path: Path):
    git = pytest.importorskip("git")

    if not path.is_dir():
        return "swh:1:cnt:" + str(git.Git().hash_object(path))
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = git.Repo.init(tmpdir)
        g = git.Git(path)  # path is working dir
        g.set_persistent_git_options(git_dir=repo.git_dir)
        g.add(".")
        return "swh:1:dir:" + str(g.write_tree())


def test_a_file():
    a_file = SNAPSHOT_CASE / "just_a_file.txt"
    assert get_swhid_from_git(a_file) == util.swhid_from_path(a_file)


def test_a_baseprint():
    bp = SNAPSHOT_CASE / "smallest"
    assert get_swhid_from_git(bp) == util.swhid_from_path(bp)


def test_with_hidden_file():
    with pytest.warns(UserWarning):
        bp = SNAPSHOT_CASE / "with_hidden_file"
        assert get_swhid_from_git(bp) != util.swhid_from_path(bp)


def test_with_hidden_dir():
    with pytest.warns(UserWarning):
        bp = SNAPSHOT_CASE / "with_hidden_dir"
        assert get_swhid_from_git(bp) != util.swhid_from_path(bp)


def test_with_exec_bit():
    with pytest.warns(UserWarning):
        bp = SNAPSHOT_CASE / "with_exec_bit"
        assert get_swhid_from_git(bp) != util.swhid_from_path(bp)
