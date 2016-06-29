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
from .EnvironmentVariable import EnvironmentVariable

MSC_LDK_GIT_MIRROR = EnvironmentVariable("MSC_LDK_GIT_SERVER", "MSC LDK Git Server.", "ssh://gitolite@msc-git02.msc-ge.com:9418/")

class GitRepository(git.Repo):
    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self._working_tree_dir)
    def get_branch_names(self):
        """
        Return a list of existing branch names for this repository
        """
        return [b.name for b in self.branches]
    def get_tag_names(self, commit_id=None):
        """
        Return a list of existing tag names for this repository.
        When commit_id is None: return all available TAGS.
        Otherwise return all TAGS pointing at commit_id
        """
        if commit_id is None:
            return [t.name for t in self.tags]
        else:
            return self.git.tag("--points-at", commit_id).split()
    def create_tag(self, tag_name, tag_message=None):
        """
        Create a tag named tag_name at head.
        When tag_message is not None: Use it to create an annotated tag
        When tag_message is None: Create a lightweight tag
        """
        if tag_name not in self.get_tag_names():
            super(self.__class__, self).create_tag(tag_name, message=tag_message)
        return tag_name
    def push(self, with_tags=False, where_to="origin"):
        """
        Push to the remote repository
        """
        if with_tags:
            self.remotes[where_to].push("--tags")
        else:
            self.remotes[where_to].push()
    # 23.06.2016: TODO: delete the commented out methods below when we are sure that they are not required
    # def get_commit_of_head(self):
    #     """
    #     Get the SHA-1 hash for the head commit
    #     """
    #     return self.head.commit.hexsha
    # def create_branch(self, branch_name):
    #     """
    #     Create a branch named branch_name
    #     """
    #     self.create_head(branch_name)
    # def pull(self):
    #     """
    #     Pull from the remote repository
    #     """
    #     self.remotes.origin.pull()
    # def add_remote(self, remote_url, name="origin"):
    #     """
    #     Add a remote tracking branch for remote_url. The remote is named name.
    #     """
    #     self.create_remote(name, remote_url)
    # def delete_branch(self, branch_name):
    #     """
    #     Delete a branch named branch_name
    #     """
    #     self.delete_head(branch_name)

class MscGitRepository(GitRepository):
    def sync_to_public(self):
        """
        Sync the repository to the public mirror
        """
        self.push(with_tags=True, where_to="origin")
    def update(self):
        """
        Pull from origin
        """
        self.remotes.origin.pull()

# 23.06.2016: TODO: mirror functionality is not yet implemented...
USE_MIRROR = True
def use_mirror(use_it):
    """
    Select whether to use the fast internal git mirror
    """
    global USE_MIRROR
    USE_MIRROR = use_it

def clone(remote_url, where_to):
    """
    Clone git repository from remote_url at local path where_to
    """
    return git.Repo.clone_from(remote_url, where_to)
