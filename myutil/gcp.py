# -*- coding: utf-8 -*-
import os
from urllib import unquote

from anytree import Node, RenderTree

import myutil.exceptions
from myutil.helpers import mkdir_p


def tree_from_list(blobs, prefix='/'):
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
    for pre, fill, node in RenderTree(tree):
        print("%s%s" % (pre, node.name))


def download_blobs(blobs=[], dir=None, recursive=False):
    if len(blobs) == 1:
        return download_blob(blob=blobs[0], filename=dir)
    if len(blobs) > 1 and not os.path.isdir(dir):
        raise myutil.exceptions.CommandException('Destination URL must name a directory, bucket, or bucket '
                'subdirectory for the multiple source form of the cp command.')  # noqa: E128

    for blob in blobs:
        blob_path = unquote(blob.path.rsplit('/', 1)[-1])
        blob_dir = blob_path.rsplit('/', 1)[:1][0]
        blob_file = blob_path.rsplit('/', 1)[-1]
        local_file_path = os.path.join(dir, blob_file)
        if blob_file != blob_dir:
            local_file_path = os.path.join(os.path.join(dir, blob_dir), blob_file)
        if (not recursive):
            local_file_path = dir
            if os.path.isdir(dir):
                local_file_path = os.path.join(dir, blob_file)
        if not os.path.dirname(local_file_path) == '':
            mkdir_p(os.path.dirname(local_file_path))
        download_blob(blob=blob, filename=local_file_path)


def download_blob(blob, filename):
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
