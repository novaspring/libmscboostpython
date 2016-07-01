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
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os
import subprocess

import pytest

import MscBoost.Git as Git
import MscBoost.Util as Util

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

def test_mirror():
    assert Git.USE_MIRROR
    Git.use_mirror(False)
    assert not Git.USE_MIRROR
    Git.use_mirror(True)
    assert Git.USE_MIRROR

def test_git_remotes():
    os.system("rm -fr w2")
    Git.clone("w1", "w2")
    g1 = Git.GitRepository("w1")
    g2 = Git.GitRepository("w2")
    g1.create_remote("origin", os.path.join(os.getcwd(), "w2"))
    with Util.WorkingDirectory("w1"):
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

def test_check_git_access(monkeypatch):
    def getstatusoutput_mock(cmd):
        assert cmd == "ssh -p 9418 gitolite@msc-git02.msc-ge.com info"
        return 0, "o.k"
    monkeypatch.setattr(subprocess, "getstatusoutput", getstatusoutput_mock)
    assert Git.check_git_access()
    monkeypatch.setattr(Git, "get_git_server", lambda: "huhu")
    assert Git.check_git_access()

def test_msc_git_repository():
    m1 = Git.MscGitRepository("w1")

    with Util.WorkingDirectory("w2"):
        os.system("git checkout feature/3 &> /dev/null")
        os.system("touch readme4.txt")
        os.system("git add readme4.txt")
        os.system("git commit -m'4nd' > /dev/null")
    m1.update()
    with Util.WorkingDirectory("w1"):
        os.system("touch readme5.txt")
        os.system("git add readme5.txt")
        os.system("git commit -m'5th' > /dev/null")
    m1.sync_to_public()
    m1.delete_remote("origin")

    # Sync Target calculation
    sync_server = "ssh://gitolite@msc-git02.msc-ge.com:9418"
    origin_url = "gitosis@msc-aac-debian01.msc-ge.mscnet:/msc/0000/libMscBoostPython.git"
    assert m1._get_sync_target(sync_server, origin_url) == "ssh://gitolite@msc-git02.msc-ge.com:9418/msc/0000/libMscBoostPython.git"
    sync_server = "ssh://gitolite@msc-git02.msc-ge.com:9418/"
    assert m1._get_sync_target(sync_server, origin_url) == "ssh://gitolite@msc-git02.msc-ge.com:9418/msc/0000/libMscBoostPython.git"

    origin_url = "git://msc-aac-debian01.msc-ge.mscnet/msc/0000/libMscBoostPython.git"
    assert m1._get_sync_target(sync_server, origin_url) == "ssh://gitolite@msc-git02.msc-ge.com:9418/msc/0000/libMscBoostPython.git"
    with Util.WorkingDirectory("w1"):
        m1.create_remote("origin", origin_url)
        assert m1._get_sync_target(sync_server) == "ssh://gitolite@msc-git02.msc-ge.com:9418/msc/0000/libMscBoostPython.git"
        m1.delete_remote("origin")
