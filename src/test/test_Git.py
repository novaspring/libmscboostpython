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

import pytest

import MscBoost.Git as Git
import MscBoost.Util as Util

def setup_test_repo():
    os.system("rm -fr w1")
    os.makedirs("w1")
    with Util.WorkingDirectory("w1"):
        os.system("git init")
        os.system("touch readme.txt")
        os.system("git add readme.txt")
        os.system("git commit -m'1st'")

def test_repository():
    setup_test_repo()
    g = Git.GitRepository("w1")
    print(g)
    assert g.GetTags() == []
    assert g.GetBranches() == ["master"]
    g.CreateTag("root")
    g.CreateTag("root") # Repeated creation is possible
    assert g.GetTags() == ["root"]
    assert g.GetTags(g.GetCommitOfHead()) == ["root"]
    with Util.WorkingDirectory("w1"):
        os.system("touch readme2.txt")
        os.system("git add readme2.txt")
        os.system("git commit -m'2nd'")
    assert g.GetTags(g.GetCommitOfHead()) == []
    g.CreateBranch("develop")
    assert g.GetBranches() == ["develop", "master"]
    g.DeleteBranch("develop")
    assert g.GetBranches() == ["master"]

def test_mirror():
    assert Git.USE_MIRROR
    Git.UseMirror(False)
    assert not Git.USE_MIRROR
    Git.UseMirror(True)
    assert Git.USE_MIRROR

def test_git_remotes():
    os.system("rm -fr w2")
    Git.Clone("w1", "w2")
    g1 = Git.GitRepository("w1")
    g2 = Git.GitRepository("w2")
    g1.AddRemote(os.path.join(os.getcwd(), "w2"))
    with Util.WorkingDirectory("w1"):
        os.system("git checkout -b feature/3")
        os.system("git push --set-upstream origin feature/3") # Push new created branch
        os.system("git tag w1-tag")
        os.system("touch readme3.txt")
        os.system("git add readme3.txt")
        os.system("git commit -m'3rd'")
    g1.Push()
    assert g1.GetTags() == ["root", "w1-tag"]
    assert g2.GetTags() == ["root"]
    g1.Push(withTags=True)
    assert g2.GetTags() == ["root", "w1-tag"]

def test_msc_git_repository():
    m1 = Git.MscGitRepository("w1")
    g2 = Git.GitRepository("w2")
    with Util.WorkingDirectory("w2"):
        os.system("git checkout feature/3")
        os.system("touch readme4.txt")
        os.system("git add readme4.txt")
        os.system("git commit -m'4nd'")
    m1.Update()
    with Util.WorkingDirectory("w1"):
        os.system("touch readme5.txt")
        os.system("git add readme5.txt")
        os.system("git commit -m'5th'")
    m1.SyncToPublic()
    m1.DeleteRemote("origin")
