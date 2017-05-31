# ----------------------------------------------------------------------------------
#  Title      : git tests
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : test_Git.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-14
# ----------------------------------------------------------------------------------
#  Description: Git tests
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016-2017 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os
import subprocess

import pytest

import MscBoost.Git as Git
import MscBoost.Util as Util
from MscBoost.Logging import Log

def setup_test_repo():
    os.system("rm -fr w1")
    os.makedirs("w1")
    with Util.WorkingDirectory("w1"):
        os.system("git init > /dev/null")
        os.system("touch readme.txt")
        os.system("git add readme.txt")
        os.system("git commit -m'1st' > /dev/null")

def test_git_exception():
    e = Git.GitException("the-exception")
    assert str(e) == "GitException: the-exception"

def test_repository():
    setup_test_repo()
    g = Git.GitRepository("w1")
    assert g.get_tag_names() == []
    assert g.get_branch_names() == ["master"]
    assert g.create_unique_tag("root") == "root"
    # Repeated creation is possible
    assert g.create_unique_tag("root") == "root"
    assert g.get_tag_names() == ["root"]
    assert g.get_tag_names(g.head.commit.hexsha) == ["root"]
    g.create_unique_tag("root_with_msg", tag_message="msg_for_tag")
    assert g.tags.root_with_msg.tag.message == "msg_for_tag"
    with Util.WorkingDirectory("w1"):
        os.system("touch readme2.txt")
        os.system("git add readme2.txt")
        os.system("git commit -m'2nd' > /dev/null")
    assert g.get_tag_names(g.head.commit.hexsha) == []
    g.create_head("develop")
    assert g.get_branch_names() == ["develop", "master"]
    g.delete_head("develop")
    assert g.get_branch_names() == ["master"]
    assert g.create_unique_tag("tag_two") == "tag_two"
    assert g.create_unique_tag("tag_two") == "tag_two"
    with pytest.raises(Git.GitException):
        g.create_unique_tag("root")
    g.get_sha1_for_version("tag_two") == g.get_head_sha1()

def test_branch_and_tag_info():
    g = Git.GitRepository("w1")
    assert g.get_branch_and_tag_info() == ("master", ("tag_two",))
    g.git.checkout("root")
    assert g.get_branch_and_tag_info() == ("master", ("root", "root_with_msg"))
    g.git.checkout("master")
    assert g.get_branch_and_tag_info() == ("master", ("tag_two",))
    assert g.get_checkout_info_string() == "Branch: master, TAG: tag_two"

def test_git_remotes():
    os.system("rm -fr w2")
    Git.clone("w1", "w2")
    g1 = Git.GitRepository("w1")
    g2 = Git.GitRepository("w2")
    g1.create_remote("origin", os.path.join(os.getcwd(), "w2"))
    assert g1.get_branch_names() == ["master"]
    with Util.WorkingDirectory("w1"):
        os.system("git push origin master")
        os.system("git checkout -b feature/3 &> /dev/null")
        os.system("git push --set-upstream origin feature/3 &> /dev/null")  # Push new created branch
        os.system("git tag w1-tag")
        os.system("touch readme3.txt")
        os.system("git add readme3.txt")
        os.system("git commit -m'3rd' > /dev/null")
    g1.push()
    assert g1.get_tag_names() == ["root", "root_with_msg", "tag_two", "w1-tag"]
    assert g2.get_tag_names() == ["root", "root_with_msg", "tag_two"]
    g1.push(with_tags=True)
    assert g2.get_tag_names() == ["root", "root_with_msg", "tag_two", "w1-tag"]
    remote_branch_names = g1.get_branch_names(local=False, remote=True)
    assert remote_branch_names == ["feature/3", "master"]
    assert g1.get_branch_names(local=False, remote=False) == []
    assert g1.get_branch_names() == ["feature/3", "master"]
    g1.push(all=True)

def test_check_git_access(monkeypatch, capsys):
    ssh_test_cmd = "ssh -p 9418 gitolite@msc-git02.msc-ge.com info"
    monkeypatch.setenv("MSC_GIT_SERVER", "ssh://gitolite@msc-git02.msc-ge.com:9418")
    def getstatusoutput_mock(cmd):
        assert cmd == ssh_test_cmd
        return 0, "o.k"
    monkeypatch.setattr(subprocess, "getstatusoutput", getstatusoutput_mock)
    assert Git.check_git_access()
    monkeypatch.setattr(Log(), "out_level", 2)
    assert Git.check_git_access(dry_run=True)
    out, err = capsys.readouterr()
    assert out == "check_git_access: %s\n" % ssh_test_cmd
    monkeypatch.setattr(Git, "get_git_server", lambda: "huhu")
    assert Git.check_git_access()

def test_msc_git_repository(capsys):
    m1 = Git.MscGitRepository("w1")

    with Util.WorkingDirectory("w2"):
        os.system("git checkout feature/3 &> /dev/null")
        os.system("touch readme4.txt")
        os.system("git add readme4.txt")
        os.system("git commit -m'4nd' > /dev/null")
    assert m1.update() is True
    with Util.WorkingDirectory("w1"):
        os.system("touch readme5.txt")
        os.system("git add readme5.txt")
        os.system("git commit -m'5th' > /dev/null")
    m1.sync_to_public(dry_run=True)
    m1.delete_remote("origin")

    # origin does no longer exist -> update must fail
    assert m1.update() is False
    out, err = capsys.readouterr()
    assert err == "ERROR: '%s': 'IterableList' object has no attribute 'origin'\n" % m1._working_tree_dir

    # Sync Target calculation
    sync_server = "ssh://gitolite@msc-git02.msc-ge.com:9418"
    origin_url = "git@destsm3ux05bbct.emea.avnet.com:7999/msc_0000/libmscboostpython.git"
    assert m1._get_sync_target(sync_server, origin_url) == "ssh://gitolite@msc-git02.msc-ge.com:9418/msc_0000/libmscboostpython.git"
    sync_server = "ssh://gitolite@msc-git02.msc-ge.com:9418/"
    assert m1._get_sync_target(sync_server, origin_url) == "ssh://gitolite@msc-git02.msc-ge.com:9418/msc_0000/libmscboostpython.git"

    origin_url = "git://msc-aac-debian01.msc-ge.mscnet/msc_0000/libmscboostpython.git"
    assert m1._get_sync_target(sync_server, origin_url) == "ssh://gitolite@msc-git02.msc-ge.com:9418/msc_0000/libmscboostpython.git"
    with Util.WorkingDirectory("w1"):
        m1.create_remote("origin", origin_url)
        assert m1._get_sync_target(sync_server) == "ssh://gitolite@msc-git02.msc-ge.com:9418/msc_0000/libmscboostpython.git"
        m1.delete_remote("origin")

def git_url(file_path):
    url = "file://%s/" % os.path.abspath(file_path)
    return url

def test_git_server_cache_variable(monkeypatch):
    # MSC_GIT_SERVER_CACHE is unset
    assert Git.get_git_server_cache() is None
    git_server_url = git_url("w1")
    # MSC_GIT_SERVER_CACHE ends with '/'
    monkeypatch.setenv("MSC_GIT_SERVER_CACHE", git_server_url)
    assert Git.get_git_server_cache() == git_server_url
    # MSC_GIT_SERVER_CACHE does not end with '/'
    monkeypatch.setenv("MSC_GIT_SERVER_CACHE", git_server_url[:-1])
    assert Git.get_git_server_cache() == git_server_url

def test_clone(capsys, monkeypatch):
    monkeypatch.setattr(Log(), "out_level", 2)
    monkeypatch.setenv("MSC_GIT_SERVER", git_url("w1"))
    # a) No cache
    os.system("rm -fr w3")
    Git.clone(git_url("w1"), "w3")
    out, err = capsys.readouterr()
    assert out == ""
    g3 = Git.GitRepository("w3")
    assert g3.remotes.origin.url == git_url("w1")
    assert g3.head.commit.message == "5th\n"

    # b) Use cache
    os.system("rm -fr w3")
    monkeypatch.setenv("MSC_GIT_SERVER_CACHE", git_url("w2"))
    with Util.WorkingDirectory("w1"):
        os.system("touch readme6.txt")
        os.system("git add readme6.txt")
        os.system("git commit -m'6th' > /dev/null")

    Git.clone(git_url("w1"), "w3")
    out, err = capsys.readouterr()
    assert out == "Cloning from git cache: %s\n" % git_url("w2")
    g3 = Git.GitRepository("w3")
    assert g3.remotes.origin.url == git_url("w1")
    assert g3.head.commit.message == "6th\n"

def test_branch_name_sort():
    b1_names = ["develop", "master", "b1"]
    b1_names.sort(key=Git.branch_name_sort_key)
    assert b1_names == ["master", "develop", "b1"]

def test_detached_head_state():
    g1 = Git.GitRepository("w2")
    sha1_feature_3 = g1.git.log("--pretty=format:%H", "-1").strip()
    g1.git.checkout("master")
    sha1_master = g1.git.log("--pretty=format:%H", "-1").strip()
    with Util.WorkingDirectory("w2"):
        os.system("touch readme2a.txt")
        os.system("git add readme2a.txt")
        os.system("git commit -m'2ath' > /dev/null")
    sha1_2a = g1.git.log("--pretty=format:%H", "-1").strip()
    g1.git.checkout(sha1_2a)
    assert g1.get_branch_and_tag_info() == ("master", None)
    g1.git.checkout(sha1_master)
    assert g1.get_branch_and_tag_info() == ("master", ('tag_two', 'w1-tag'))
    assert g1.get_checkout_info_string() == "Branch: master, TAGS: tag_two, w1-tag [Detached HEAD]"
    g1.git.checkout(sha1_feature_3)
    assert g1.get_branch_and_tag_info() == ("feature/3", None)
    head_version = "tag_two-2-g%s" % sha1_feature_3[:7]
    assert g1.get_head_version() == head_version
    assert g1.get_checkout_info_string() == "Branch: feature/3 [%s] [Detached HEAD]" % head_version
    assert g1.get_active_branch_name() == "feature/3"
    assert g1.get_head_sha1() == sha1_feature_3

def test_is_dirty():
    g1 = Git.GitRepository("w1")
    with Util.WorkingDirectory("w1"):
        assert g1.is_dirty() is False
        assert g1.is_dirty(staged=False) is False
        assert g1.is_dirty(unstaged=False) is False
        assert g1.is_dirty(unstaged=False, staged=False) is False
        f = open("readme.txt", "a")
        print("read me!", file=f)
        f.close()
        assert g1.is_dirty() is True
        assert g1.is_dirty(staged=False) is True
        assert g1.is_dirty(unstaged=False) is False
        assert g1.is_dirty(unstaged=False, staged=False) is False
        os.system("git add readme.txt")
        assert g1.is_dirty() is True
        assert g1.is_dirty(staged=False) is False
        assert g1.is_dirty(unstaged=False) is True
        assert g1.is_dirty(unstaged=False, staged=False) is False

def create_git_push_repos():
    os.system("""
    rm -rf push_tmp.git push_src.git push_clone.git push_clone2.git;
    mkdir push_tmp.git &&
    cd push_tmp.git &&
    touch README.txt &&
    git init &&
    git add README.txt &&
    git commit -am initial &&
    cd .. &&
    git clone --bare push_tmp.git push_src.git &&
    git clone push_src.git push_clone.git &&
    git clone push_src.git push_clone2.git
    """)

def test_push_succeeds():
    create_git_push_repos()
    os.system("""
    cd push_clone.git &&
    touch COPYING.txt &&
    git add COPYING.txt &&
    git commit -am COPYING
    """)

    assert not os.path.isfile("push_clone2.git/COPYING.txt")
    g = Git.GitRepository("push_clone.git")
    g.push(with_tags=True, all=True)
    os.system("""cd push_clone2.git && git pull""")
    assert os.path.isfile("push_clone2.git/COPYING.txt")

def test_push_fails():
    create_git_push_repos()
    os.system("""
    cd push_clone2.git &&
    touch MAKEFILE &&
    git add MAKEFILE &&
    git commit -am MAKEFILE &&
    git push &&
    cd .. &&
    cd push_clone.git &&
    touch COPYING.txt &&
    git add COPYING.txt &&
    git commit -am COPYING
    """)

    assert not os.path.isfile("push_clone2.git/COPYING.txt")
    g = Git.MscGitRepository("push_clone.git")
    # this will conflict because one push_clone2.git already committed to push_src, so we can't push in push_clone without merging first
    with pytest.raises(Git.GitException):
        g.push(with_tags=True, all=True)

    os.system("""cd push_clone2.git && git pull""")
    # because of merge CONFLICT push must not have succeeded
    assert not os.path.isfile("push_clone2.git/COPYING.txt")
