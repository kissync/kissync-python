"""
To avoid redundant network transfers, keep a history
of files that are uploaded
"""


_history = {}


def update(localFile):
    """ Update the localFile to be the latest version transfered """
    _history[localFile.path] = localFile.checksum


def isLatest(localFile):
    """ Checks if localFile is newer than the previously transferred version """
    if localFile.path in _history:
        if localFile.checksum != _history[localFile.path]:
            return True
        else:
            return False
    else:
        return True