# -*- coding: utf-8 -*-
import click
from google.cloud import storage

import myutil.exceptions
from myutil.gcp import download_blobs, render_tree, tree_from_list
from myutil.helpers import bucket_path_from_url

storage_client = storage.Client()


@click.group()
def cli():
    """ Grouping mechanism """
    pass


@cli.command()
@click.argument('url')
def ls(url):
    """List objects in a bucket

    Keyword arguments:
    url -- The URL in the format gs://bucket/subdir
    """

    (bucket_name, prefix) = bucket_path_from_url(url)
    bucket = storage_client.get_bucket(bucket_name)
    blob_tree = tree_from_list(bucket.list_blobs(prefix=prefix), prefix)
    render_tree(blob_tree)


@cli.command()
@click.option('--recursive', '-r', default=False, is_flag=True)
@click.argument('url')
@click.argument('dir')
def cp(recursive, url, dir):
    """Copy blobs from a bucket

    Keyword arguments:
    url -- The URL in the format gs://bucket/subdir
    dir -- The dir to copy to. If recursive, it will create
    """

    (bucket_name, prefix) = bucket_path_from_url(url)
    bucket = storage_client.get_bucket(bucket_name)
    blobs = [blob for blob in bucket.list_blobs(prefix=prefix)]  # HTTPIterator to list

    if len(blobs) == 0:
        raise myutil.exceptions.CommandException('No URLs matched: {}'.format(url))
    if not recursive and len(blobs) > 1:
        print('Omitting prefix "gs://{}/{}/". (Did you mean to do cp -r?)'.format(bucket.name, prefix))
        raise myutil.exceptions.CommandException('No URLs matched')

    download_blobs(blobs=blobs, dir=dir, prefix=prefix, recursive=recursive)


if __name__ == '__main__':
    cli()
