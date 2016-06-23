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
    assert g.get_tags() == []
    assert g.get_branches() == ["master"]
    g.create_tag("root")
    g.create_tag("root")  # Repeated creation is possible
    assert g.get_tags() == ["root"]
    assert g.get_tags(g.get_commit_of_head()) == ["root"]
    with Util.WorkingDirectory("w1"):
        os.system("touch readme2.txt")
        os.system("git add readme2.txt")
        os.system("git commit -m'2nd'")
    assert g.get_tags(g.get_commit_of_head()) == []
    g.create_branch("develop")
    assert g.get_branches() == ["develop", "master"]
    g.delete_branch("develop")
    assert g.get_branches() == ["master"]

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
    g1.add_remote(os.path.join(os.getcwd(), "w2"))
    with Util.WorkingDirectory("w1"):
        os.system("git checkout -b feature/3")
        os.system("git push --set-upstream origin feature/3")  # Push new created branch
        os.system("git tag w1-tag")
        os.system("touch readme3.txt")
        os.system("git add readme3.txt")
        os.system("git commit -m'3rd'")
    g1.push()
    assert g1.get_tags() == ["root", "w1-tag"]
    assert g2.get_tags() == ["root"]
    g1.push(with_tags=True)
    assert g2.get_tags() == ["root", "w1-tag"]

def test_msc_git_repository():
    m1 = Git.MscGitRepository("w1")
    with Util.WorkingDirectory("w2"):
        os.system("git checkout feature/3")
        os.system("touch readme4.txt")
        os.system("git add readme4.txt")
        os.system("git commit -m'4nd'")
    m1.update()
    with Util.WorkingDirectory("w1"):
        os.system("touch readme5.txt")
        os.system("git add readme5.txt")
        os.system("git commit -m'5th'")
    m1.sync_to_public()
    m1.delete_remote("origin")
