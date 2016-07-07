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

import subprocess

import git
from .EnvironmentVariable import EnvironmentVariable

MSC_PUBLIC_GIT_SERVER = "ssh://gitolite@msc-git02.msc-ge.com:9418/"
MSC_GIT_SERVER_CACHE = EnvironmentVariable("MSC_GIT_SERVER_CACHE", "MSC Git Server Cache.")

class GitException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return "GitException: %s" % self.msg

class GitRepository(git.Repo):
    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self._working_tree_dir)

    def get_branch_names(self, local=True, remote=False):
        """
        Return a list of existing branch names for this repository.
        When remote==True: Return known branches from remotes.origin
        """
        branch_names = []
        if local:
            branch_names.extend([b.name for b in self.branches])
        if remote:
            for ref in self.remotes.origin.refs:
                branch_name = ref.name.partition("/")[2]
                if branch_name != "HEAD":
                    if branch_name not in branch_names:
                        branch_names.append(branch_name)
        branch_names.sort()
        return branch_names

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

    def get_branch_and_tag_info(self):
        """
        Return the branch_name/tag_name HEAD in the repository.
        """
        sha1_maybe, ref = self.head._get_ref_info(self.head.repo, self.head.path)
        if ref is not None:
            # e.g.: (sha1_maybe==None, ref=='refs/heads/v1.0.0')
            branch_name = self.active_branch.name
            sha1_maybe = self.head.object.hexsha
        else:
            # e.g.: (sha1_maybe=='55df1ae9c0e30fb064ab8c107a7a9f767020585b', ref==None)
            branch_name = None
        tag_name = None
        for tag in self.tags:
            if tag.object.hexsha == sha1_maybe:
                # e.g.: tag_name := 'LC984_20160113_V0_4_0'
                tag_name = tag.name
        if branch_name is None and tag_name is None:
            # e.g. tag_name == 'LC984_20160504_V1_0_0'
            tag_name = self.git.describe()
        return (branch_name, tag_name)

    def get_checkout_info_string(self):
        """
        Get a descriptive info string for the current checked out branch/tag
        """
        active_branch_name, active_tag_name = self.get_branch_and_tag_info()
        branch_info = "Branch: %s" % active_branch_name if active_branch_name else None
        tag_info = "TAG: %s" % active_tag_name if active_tag_name else None
        info_list = [info for info in [branch_info, tag_info] if info]
        return ", ".join(info_list)

    def create_unique_tag(self, tag_name, tag_message=None):
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
                raise GitException("%s: TAG '%s' does already exist in commit history" % (self, tag_name))
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

def get_git_server():
    msc_git_server = MSC_GIT_SERVER_CACHE.get_value(MSC_PUBLIC_GIT_SERVER)
    return msc_git_server

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
        msc_ldk_public_git_server = MSC_PUBLIC_GIT_SERVER
        sync_to_public_remote = "_sync_to_public"
        self.create_remote(sync_to_public_remote, self._get_sync_target(msc_ldk_public_git_server))
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

def check_git_access():
    """
    Check whether the git server can be accessed.
    """
    git_server = get_git_server()
    if git_server.startswith("ssh://"):
        git_ssh_server = git_server.partition("ssh://")[2].rstrip("/")
        ssh_server, dummy, ssh_port = git_ssh_server.partition(":")
        cmd = "ssh -p %s %s info" % (ssh_port, ssh_server)
        return subprocess.getstatusoutput(cmd)[0] == 0
    return True

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
