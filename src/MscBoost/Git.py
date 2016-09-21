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
from .Logging import Log

MSC_PUBLIC_GIT_SERVER = "ssh://gitolite@msc-git02.msc-ge.com:9418/"
MSC_GIT_SERVER = EnvironmentVariable("MSC_GIT_SERVER", "MSC Git Server.", default_value=MSC_PUBLIC_GIT_SERVER)
MSC_GIT_SERVER_CACHE = EnvironmentVariable("MSC_GIT_SERVER_CACHE", "MSC Git Server Cache.")

class GitException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return "GitException: %s" % self.msg

def branch_name_sort_key(name):
    """
    Support for branch name sorting.
    master has the highest priority, next comes devel, the other branches are sorted alphabetically
    """
    return {"master": chr(1), "develop": chr(2)}.get(name, name)

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
        Return the branch_name/tag_names HEAD in the repository.
        Return the branch name and a tuple of all matching tag names. When no tag names are found: None is returned as tag_names.
        """
        # pylama:ignore=C901: C901 'GitRepository.get_branch_and_tag_info' is too complex (11) [mccabe]
        sha1_maybe, ref = self.head._get_ref_info(self.head.repo, self.head.path)
        if ref is not None:
            # e.g.: (sha1_maybe==None, ref=='refs/heads/v1.0.0')
            branch_name = self.active_branch.name
            sha1_maybe = self.head.object.hexsha
        else:
            # e.g.: (sha1_maybe=='55df1ae9c0e30fb064ab8c107a7a9f767020585b', ref==None)
            # Detached head state:
            # run git log <branchname> to find the branch that contains sha1_maybe
            branch_names = sorted(self.get_branch_names(), key=branch_name_sort_key)
            branch_name = None
            for b_name in branch_names:
                if sha1_maybe in self.git.log('--pretty=format:%H', b_name):
                    branch_name = b_name
                    break
            if branch_name is None:
                # When the above test didn't succeed:
                # run git log <origin/branchname> to find the branch that contains sha1_maybe
                remote_branch_names = self.get_branch_names(local=False, remote=True)
                for b_name in branch_names:
                    if b_name in remote_branch_names:
                        if sha1_maybe in self.git.log('--pretty=format:%H', "origin/" + b_name):
                            branch_name = b_name
                            break
        tag_names = []
        tag_string = self.git.log('--pretty=format:%d', sha1_maybe, "-1").strip(" ()\n")
        for tag_candidate in tag_string.split(","):
            tag_candidate = tag_candidate.strip()
            if tag_candidate.startswith("tag: "):
                tag_names.append(tag_candidate[5:])
        if tag_names:
            tag_names.sort()
            tag_names = tuple(tag_names)
        else:
            tag_names = None
        return (branch_name, tag_names)

    def get_checkout_info_string(self):
        """
        Get a descriptive info string for the current checked out branch/tag
        """
        active_branch_name, active_tag_names = self.get_branch_and_tag_info()
        branch_info = "Branch: %s" % active_branch_name if active_branch_name else None
        if active_tag_names:
            if len(active_tag_names) == 1:
                tag_info = "TAG: %s" % active_tag_names
            else:
                tag_info = "TAGS: %s" % ", ".join(active_tag_names)
        else:
            tag_info = None
        info_list = [info for info in [branch_info, tag_info] if info]
        info_string = ", ".join(info_list)
        head_version = self.get_head_version()
        if head_version not in (active_tag_names or []):
            info_string += " [%s]" % head_version
        ref = self.head._get_ref_info(self.head.repo, self.head.path)[1]
        if ref is None:
            info_string += " [Detached HEAD]"
        return info_string

    def get_active_branch_name(self):
        """
        Get the name of the active branch name.
        """
        return self.get_branch_and_tag_info()[0]

    def get_head_sha1(self):
        """
        Get SHA1 of git HEAD.
        """
        return self.head.object.hexsha

    def get_head_version(self):
        """
        Get a tag based version string of HEAD.
        """
        return self.git.describe("--tags", "--dirty", "--always")

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

def get_git_server():
    """
    Get the MSC git server. The value can be overriden by the MSC_GIT_SERVER environment variable.
    It is assured that this server address ends using '/'
    """
    msc_git_server = MSC_GIT_SERVER.get_value()
    if not msc_git_server.endswith("/"):
        msc_git_server += "/"
    return msc_git_server

def get_git_server_cache():
    """
    Get the MSC git server cache. The value can be overriden by the MSC_GIT_SERVER_CACHE environment variable.
    It is assured that this server address ends using '/'
    When MSC_GIT_SERVER_CACHE is unset, None is returned
    """
    msc_git_server_cache = MSC_GIT_SERVER_CACHE.get_value()
    if msc_git_server_cache:
        if not msc_git_server_cache.endswith("/"):
            msc_git_server_cache += "/"
    return msc_git_server_cache

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
        path_start_idx = min(i for i in [origin_url.find("/"), origin_url.find(":")] if i >= 0)
        path_spec = origin_url[path_start_idx:].lstrip(":/")
        sync_target_url = sync_server + path_spec
        return sync_target_url

    def sync_to_public(self, dry_run=False):
        """
        Sync the repository to the public mirror
        """
        msc_ldk_public_git_server = MSC_PUBLIC_GIT_SERVER
        sync_to_public_remote = "_sync_to_public"
        sync_target = self._get_sync_target(msc_ldk_public_git_server)
        Log().out(2, "sync_to_public: %s -> %s" % (self.remotes.origin.url, sync_target))
        if not dry_run:
            if sync_to_public_remote in [r.name for r in self.remotes]:
                # Delete remote when it does already exist
                self.delete_remote(sync_to_public_remote)
            self.create_remote(sync_to_public_remote, sync_target)
            self.push(with_tags=True, all=True, where_to=sync_to_public_remote)
            self.delete_remote(sync_to_public_remote)

    def update(self):
        """
        Pull from origin
        """
        self.remotes.origin.pull()

def check_git_access(dry_run=False):
    """
    Check whether the git server can be accessed.
    """
    git_server = get_git_server()
    if git_server.startswith("ssh://"):
        git_ssh_server = git_server.partition("ssh://")[2].rstrip("/")
        ssh_server, dummy, ssh_port = git_ssh_server.partition(":")
        cmd = "ssh -p %s %s info" % (ssh_port, ssh_server)
        Log().out(2, "check_git_access: %s" % cmd)
        if not dry_run:
            return subprocess.getstatusoutput(cmd)[0] == 0
    return True

def clone(remote_url, where_to):
    """
    Clone git repository from remote_url at local path where_to
    Respects MSC_GIT_SERVER and MSC_GIT_SERVER_CACHE
    """
    git_server = get_git_server()
    repo = None
    if remote_url.startswith(git_server):
        git_server_cache = get_git_server_cache()
        if git_server_cache is not None:
            relative_url = remote_url[len(git_server):]
            cached_remote_url = git_server_cache + relative_url
            Log().out(2, "Cloning from git cache: %s" % cached_remote_url)
            repo = git.Repo.clone_from(cached_remote_url, where_to)
            # Replace git cache url by the server url
            origin = repo.remotes.origin
            cw = origin.config_writer
            cw.set("url", remote_url)
            cw.release()
            origin.pull()
    if repo is None:
        repo = git.Repo.clone_from(remote_url, where_to)
    return repo
