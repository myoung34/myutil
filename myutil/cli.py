# -*- coding: utf-8 -*-
import click
from google.cloud import storage

import myutil.exceptions
from myutil.gcp import download_blobs, render_tree, tree_from_list

storage_client = storage.Client()


@click.group()
def cli():
    """ Grouping mechanism """
    pass


def validate_and_parse(url):
    """ Validate the URL given starts with the GCP gs:// protocol
    and break it into bucket and the non-bucket pieces"""

    if not url.startswith('gs://'):
        raise Exception('invalid URL {}'.format(url))
    url_parts = url.replace('gs://', '').split('/', 1)
    return (storage_client.get_bucket(url_parts[0]), url_parts[1])


@cli.command()
@click.argument('url')
def ls(url):
    """List objects in a bucket

    Keyword arguments:
    url -- The URL in the format gs://bucket/subdir
    """

    (bucket, prefix) = validate_and_parse(url)
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

    (bucket, prefix) = validate_and_parse(url)
    blobs = [blob for blob in bucket.list_blobs(prefix=prefix)]

    if len(blobs) == 0:
        raise myutil.exceptions.CommandException('No URLs matched: {}'.format(url))
    if not recursive and len(blobs) > 1:
        print('Omitting prefix "gs://{}/{}/". (Did you mean to do cp -r?)'.format(bucket.name, prefix))
        raise myutil.exceptions.CommandException('No URLs matched')

    download_blobs(blobs=blobs, dir=dir, recursive=recursive)


if __name__ == '__main__':
    cli(obj={})
