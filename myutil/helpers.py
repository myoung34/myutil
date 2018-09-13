# -*- coding: utf-8 -*-
import errno
import os


def mkdir_p(path):
    """Helper method to mkdir recursively (similar to `mkdir -p`

    Keyword arguments:
    path -- string path to create
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
