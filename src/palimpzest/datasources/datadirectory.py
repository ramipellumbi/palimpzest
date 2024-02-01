from palimpzest.elements import DataRecord
from .loaders import DirectorySource, FileSource

import os
import pickle

class _DataDirectory:
    """The DataDirectory is a registry of data sources."""

    def __init__(self, configDir, create=False):
        self._registry = {}
        self._cache = {}
        self._tempCache = {}

        self._configDir = configDir
        if create:
            if not os.path.exists(configDir):
                os.makedirs(configDir)
                os.makedirs(configDir + "/registered")
                os.makedirs(configDir + "/cache")
                pickle.dump(self._registry, open(configDir + "/cache/registry.pkl", "wb"))

        # Unpickle the registry of data sources
        if os.path.exists(configDir + "/cache/registry.pkl"):
            self._registry = pickle.load(open(configDir + "/cache/registry.pkl", "rb"))

        # Iterate through all items in the cache directory, and rebuild the table of entries
        for root, dirs, files in os.walk(configDir + "/cache"):
            for file in files:
                if file.endswith(".cached"):
                    uniqname = file[:-7]
                    self._cache[uniqname] = root + "/" + file

    #
    # These methods handle properly registered data files, meant to be kept over the long haul
    #
    def registerLocalDirectory(self, path, uniqName):
        """Register a local directory as a data source."""
        self._registry[uniqName] = ("dir", path)
        pickle.dump(self._registry, open(self._configDir + "/cache/registry.pkl", "wb"))

    def registerLocalFile(self, path, uniqName):
        """Register a local file as a data source."""
        self._registry[uniqName] = ("file", path)
        pickle.dump(self._registry, open(self._configDir + "/cache/registry.pkl", "wb"))

    def getRegisteredDataset(self, uniqName):
        """Return a dataset from the registry."""
        if not uniqName in self._registry:
            return None
        
        entry, path = self._registry[uniqName]
        if entry == "dir":
            return DirectorySource(path)
        elif entry == "file":
            return FileSource(path)
        else:
            raise Exception("Unknown entry type")

    #
    # These methods handle cached results. They are meant to be persisted for performance reasons,
    # but can always be recomputed if necessary.
    #
    def getCachedResult(self, uniqName):
        """Return a cached result."""
        if not uniqName in self._cache:
            return None
        
        cachedResult = pickle.load(open(self._cache[uniqName], "rb"))
        def iterateOverCachedResult():
            for x in cachedResult:
                yield x
        return iterateOverCachedResult()
    
    def clearCache(self):
        """Clear the cache."""
        self._cache = {}
        self._tempCache = {}

        # Delete all files in the cache directory
        for root, dirs, files in os.walk(self._configDir + "/cache"):
            for file in files:
                os.remove(root + "/" + file)

    def hasCachedAnswer(self, uniqName):
        """Check if a dataset is in the cache."""
        return uniqName in self._cache

    def openCache(self, cacheId):
        if not cacheId in self._cache and not cacheId in self._tempCache:
            self._tempCache[cacheId] = []
            return True
        return False

    def appendCache(self, cacheId, data):
        self._tempCache[cacheId].append(data)

    def closeCache(self, cacheId):
        """Close the cache."""
        filename = self._configDir + "/cache/" + cacheId + ".cached"
        pickle.dump(self._tempCache[cacheId], open(filename, "wb"))
        del self._tempCache[cacheId]
        self._cache[cacheId] = filename

_DataDirectoryMember = None
def initDataDirectory(initDir, create=False):
    """Initialize the DataDirectory with a directory."""
    global _DataDirectoryMember
    if not _DataDirectoryMember is None:
        raise Exception("DataDirectory already initialized")
    else:
        _DataDirectoryMember = _DataDirectory(initDir, create=create)

def DataDirectory():
    return _DataDirectoryMember