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
    def __init__(self, working_directory):
        self.repo = git.Repo(working_directory)
    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.repo._working_tree_dir)
    def get_branches(self):
        """
        Return a list of existing branch names for this repository
        """
        return [b.name for b in self.repo.branches]
    def get_tags(self, commit_id=None):
        """
        Return a list of existing tag names for this repository.
        When commit_id is None: return all available TAGS.
        Otherwise return all TAGS pointing at commit_id
        """
        if commit_id is None:
            return [t.name for t in self.repo.tags]
        else:
            return self.repo.git.tag("--points-at", commit_id).split()
    def get_commit_of_head(self):
        """
        Get the SHA-1 hash for the head commit
        """
        return self.repo.head.commit.hexsha
    def create_tag(self, tag_name):
        """
        Create a tag named tag_name at head
        """
        if tag_name not in self.get_tags():
            self.repo.create_tag(tag_name)
        return tag_name
    def create_branch(self, branch_name):
        """
        Create a branch named branch_name
        """
        self.repo.create_head(branch_name)
    def push(self, with_tags=False, where_to="origin"):
        """
        Push to the remote repository
        """
        if with_tags:
            self.repo.remotes[where_to].push("--tags")
        else:
            self.repo.remotes[where_to].push()
    def pull(self):
        """
        Pull from the remote repository
        """
        self.repo.remotes.origin.pull()
    def add_remote(self, remote_url, name="origin"):
        """
        Add a remote tracking branch for remote_url. The remote is named name.
        """
        self.repo.create_remote(name, remote_url)
    def delete_remote(self, name):
        """
        Remove a remote tracking branch named name.
        """
        self.repo.delete_remote(name)
    def delete_branch(self, branch_name):
        """
        Delete a branch named branch_name
        """
        self.repo.delete_head(branch_name)

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
        self.pull()

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
