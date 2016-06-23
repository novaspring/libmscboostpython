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
        os.system("git init > /dev/null")
        os.system("touch readme.txt")
        os.system("git add readme.txt")
        os.system("git commit -m'1st' > /dev/null")

def test_repository():
    setup_test_repo()
    g = Git.GitRepository("w1")
    assert g.get_tag_names() == []
    assert g.get_branch_names() == ["master"]
    g.create_tag("root")
    g.create_tag("root")  # Repeated creation is possible
    assert g.get_tag_names() == ["root"]
    assert g.get_tag_names(g.head.commit.hexsha) == ["root"]
    with Util.WorkingDirectory("w1"):
        os.system("touch readme2.txt")
        os.system("git add readme2.txt")
        os.system("git commit -m'2nd' > /dev/null")
    assert g.get_tag_names(g.head.commit.hexsha) == []
    g.create_head("develop")
    assert g.get_branch_names() == ["develop", "master"]
    g.delete_head("develop")
    assert g.get_branch_names() == ["master"]

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
    assert g1.get_tag_names() == ["root", "w1-tag"]
    assert g2.get_tag_names() == ["root"]
    g1.push(with_tags=True)
    assert g2.get_tag_names() == ["root", "w1-tag"]

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
