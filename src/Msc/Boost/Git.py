# ----------------------------------------------------------------------------------
#  Title      : Git support
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : Git.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-09
# ----------------------------------------------------------------------------------
#  Description: Git support
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import git

class GitRepository(object):
    def __init__(self, workingDirectory):
        self.repo = git.Repo(workingDirectory)
    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.repo._working_tree_dir)
    def GetBranches(self):
        """
        Return a list of existing branch names for this repository
        """
        return [b.name for b in self.repo.branches]
    def GetTags(self, commitId=None):
        """
        Return a list of existing tag names for this repository.
        When commitId is None: return all available TAGS.
        Otherwise return all TAGS pointing at commitId
        """
        if commitId is None:
            return [t.name for t in self.repo.tags]
        else:
            return self.repo.git.tag("--points-at", commitId).split()
    def GetCommitOfHead(self):
        """
        Get the SHA-1 hash for the head commit
        """
        return self.repo.head.commit.hexsha
    def CreateTag(self, tagName):
        """
        Create a tag named tagName at head
        """
        if not tagName in self.GetTags():
            self.repo.create_tag(tagName)
        return tagName
    def CreateBranch(self, branchName):
        """
        Create a branch named branchName
        """
        self.repo.create_head(branchName)
    def Push(self, withTags=False, whereTo="origin"):
        """
        Push to the remote repository
        """
        if withTags:
            self.repo.remotes[whereTo].push("--tags")
        else:
            self.repo.remotes[whereTo].push()
    def Pull(self):
        """
        Pull from the remote repository
        """
        self.repo.remotes.origin.pull()
    def AddRemote(self, remoteUrl, name="origin"):
        """
        Add a remote tracking branch for remoteUrl. The remote is named name.
        """
        self.repo.create_remote(name, remoteUrl)
    def DeleteRemote(self, name):
        """
        Remove a remote tracking branch named name.
        """
        self.repo.delete_remote(name)
    def DeleteBranch(self, branchName):
        """
        Delete a branch named branchName
        """
        self.repo.delete_head(branchName)

class MscGitRepository(GitRepository):
    def SyncToPublic(self):
        """
        Sync the repository to the public mirror
        """
        self.Push(withTags=True, whereTo="origin")
    def Update(self):
        """
        Pull from origin
        """
        self.Pull()

USE_MIRROR = True
def UseMirror(useIt):
    """
    Select whether to use the fast internal git mirror
    """
    global USE_MIRROR
    USE_MIRROR = useIt

def Clone(remoteUrl, whereTo):
    """
    Clone git repository from remoteUrl at local path whereTo
    """
    return git.Repo.clone_from(remoteUrl, whereTo)

# r = GitRepository("/big/yocto/0000/libMscBoostPython")
# m = MscGitRepository("/big/yocto/0000/libMscBoost")
