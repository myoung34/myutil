# -*- coding: utf-8 -*-
import errno
import os


def bucket_path_from_url(url=None):
    """ Validate the URL given starts with the GCP gs:// protocol
    and break it into bucket and the non-bucket pieces"""

    if not url.startswith('gs://'):
        raise Exception('invalid URL {}'.format(url))
    url_parts = url.replace('gs://', '').split('/', 1)
    if len(url_parts) < 2:
        raise Exception('invalid URL {}'.format(url))
    return (url_parts[0], url_parts[1])


def mkdir_p(path):
    """Helper method to mkdir recursively (similar to `mkdir -p`

    Keyword arguments:
    path -- string path to create
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if not exc.errno == errno.EEXIST and not os.path.isdir(path):
            raise
