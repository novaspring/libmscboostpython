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

MSC_LDK_GIT_SERVER = EnvironmentVariable("MSC_LDK_GIT_SERVER", "MSC LDK Git Server.", "ssh://gitolite@msc-git02.msc-ge.com:9418/")

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
            # a) a new TAG
            super(self.__class__, self).create_tag(tag_name, message=tag_message)
        else:
            # b) an existing TAG
            if self.tags[tag_name].commit == self.head.commit:
                # b1) All o.k.: TAG already present at HEAD
                pass
            else:
                # b2) Problem: TAG exists in commit history
                return None
        return tag_name
    def push(self, with_tags=False, all=False, where_to="origin"):
        """
        Push to the remote repository
        """
        extra_options = []
        if all:
            extra_options.append("--all")
        if with_tags:
            extra_options.append("--tags")
        if extra_options:
            # Can't use --all and --tags in one invocation -> use two invocations
            for option in extra_options:
                self.remotes[where_to].push(option)
        else:
            self.remotes[where_to].push()
    ## @TODO: delete the commented out methods below when we are sure that they are not required
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
    def _get_sync_target(self, sync_server, origin_url=None):
        """
        Derive the fully qualified sync_server URL based on origin_url.
        """
        if not sync_server.endswith("/"):
            sync_server += "/"
        if origin_url is None:
            origin_url = self.remotes.origin.url
        if "//" in origin_url:
            origin_url = origin_url.partition("//")[2]
        path_spec = origin_url.partition("/")[2]
        sync_target_url = sync_server + path_spec
        return sync_target_url

    def sync_to_public(self):
        """
        Sync the repository to the public mirror
        """
        msc_ldk_git_server = MSC_LDK_GIT_SERVER.get_value()
        sync_to_public_remote = "_sync_to_public"
        self.create_remote(sync_to_public_remote, self._get_sync_target(msc_ldk_git_server))
        ## @TODO: Check remote URL, remove debugging code, activate push + delete below
        from .Logging import Log
        import os
        from .Util import WorkingDirectory
        with WorkingDirectory(self._working_tree_dir):
            Log().notice("MscGitRepository::sync_to_public: Please check the remote URL:")
            Log().notice("%s" % os.popen("git remote -v").read())
        # self.push(with_tags=True, all=True, where_to=sync_to_public_remote)
        # self.delete_remote(sync_to_public_remote)

    def update(self):
        """
        Pull from origin
        """
        self.remotes.origin.pull()

## @TODO: mirror functionality is not yet implemented...
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
