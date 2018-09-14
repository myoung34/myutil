# -*- coding: utf-8 -*-
import os
import re
from urllib import unquote

from anytree import Node, RenderTree
from google.cloud.storage.blob import Blob

import myutil.exceptions
from myutil.helpers import mkdir_p


def tree_from_list(blobs, prefix='/'):
    """Build an anytree Tree from GCP blob objects

    Keyword arguments:
    blobs -- GCP blob objects to render
    prefix -- Initial prefix used to help with render (top-level root-node name)
    """
    root_node = Node(prefix)
    parent = root_node
    for blob in blobs:
        blob_path = unquote(blob.path.rsplit('/', 1)[-1])
        if blob_path.startswith(prefix):
            blob_path = blob_path[len(prefix):]
        for part in blob_path.split('/'):
            if len(part) == 0 or parent.name == part:
                continue
            if part in [child.name for child in parent.children]:
                parent = parent.children[0]
                continue
            last = Node(part, parent=parent)
            parent = last
        parent = root_node
    return root_node


def render_tree(tree=None):
    """Render an anytree Tree

    Keyword arguments:
    tree -- anytree Node with children
    """
    for pre, fill, node in RenderTree(tree):
        print("%s%s" % (pre, node.name))


def download_blobs(blobs=[], dir=None, prefix=None, recursive=False):
    """Download an array of GCP blob objects

    Keyword arguments:
    blobs -- GCP blob objects to download
    dir -- string directory to download into
    """
    if not recursive and len(blobs) == 1:
        return download_blob(blobs[0], dir)
    if len(blobs) > 1 and not os.path.isdir(dir):
        raise myutil.exceptions.CommandException('Destination URL must name a directory, bucket, or bucket '
                'subdirectory for the multiple source form of the cp command.')  # noqa: E128

    # First job is to shorten the tree so that the root node is where the prefix ends on
    # the URL. Ex: gs://foo/a/b should have root node 'b'
    _fixed_prefix = re.sub('/$', '', prefix)
    bucket = blobs[0].bucket
    blob_prefix = None
    root_node = Node(dir.replace('/', ''))
    for pre, fill, node in RenderTree(tree_from_list(blobs)):
        if node.name == _fixed_prefix.rsplit('/', 1)[-1]:
            # Found the first node matching the last part of our URL. Set it as the root child
            blob_prefix = os.sep.join([_node.name for _node in node.ancestors])  # preserve to use it on name rebuild
            root_node.children = [node]
            break

    # Walk the tree and rebuild filenames based on node path, cleaning up data along the way
    for pre, fill, node in RenderTree(root_node):
        if node.is_leaf:
            blob_name = re.sub('^[/]*', '', blob_prefix + os.sep + os.sep.join([_node.name for _node in node.ancestors][1:]) + os.sep + node.name).replace('//', '/')  # noqa
            filename = os.sep.join([_node.name for _node in node.ancestors]) + os.sep + node.name
            mkdir_p(os.path.dirname(filename))
            download_from_bucket(name=blob_name, bucket=bucket, filename=filename)


def download_from_bucket(name, bucket, filename):
    """Download a GCP blob object given a string filename and a bucket

    Keyword arguments:
    name -- full key name of  the GCP blob object to download
    bucket -- bucket to download from
    filename -- string filename to download into
    """
    return download_blob(blob=Blob(name=name, bucket=bucket), filename=filename)


def download_blob(blob, filename, recursive=False):
    """Download a GCP blob object

    Keyword arguments:
    blob -- GCP blob object to download
    filename -- string filename to download into
    """
    print('Copying gs://{}/{}...'.format(blob.bucket.name, blob.name))
    if filename.endswith('/'):
        if not os.path.isdir(filename):
            raise myutil.exceptions.CommandException('Skipping attempt to download to filename ending with slash '
                                                     '({}).\nThis typically happens when using gsutil to download '
                                                     'from a\nsubdirectory created by the Cloud Console\n'
                                                     '(https://cloud.google.com/console)'.format(filename))
    if os.path.isdir(filename):
        filename = os.path.join(filename, blob.name.rsplit('/', 1)[1])

    try:
        blob.download_to_filename(filename)
    except AttributeError:
        # https://github.com/GoogleCloudPlatform/google-cloud-python/issues/3736
        pass
