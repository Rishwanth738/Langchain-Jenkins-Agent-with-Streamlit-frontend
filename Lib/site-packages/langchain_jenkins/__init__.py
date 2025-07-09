from importlib import metadata


from langchain_jenkins.tools import JenkinsJobRun
from langchain_jenkins.jenkins import JenkinsAPIWrapper

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "JenkinsAPIWrapper",
    "JenkinsJobRun",
    "__version__",
]
