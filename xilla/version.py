__version__ = (2, 0, 0)
__codename__ = 'Alpaca Alpha v0'
import os
import git
try:
    branch = git.Repo(path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))).active_branch.name
except Exception:
    branch = 'master'