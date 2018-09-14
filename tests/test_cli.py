# -*- coding: utf-8 -*-
import click
import google.auth.credentials
import mock
from click.testing import CliRunner
from mock import call

import myutil.exceptions


class TestClient:
    @staticmethod
    def _get_target_class():
        from google.cloud.storage.bucket import Bucket
        return Bucket

    def _make_credentials(self):
        return mock.Mock(spec=google.auth.credentials.Credentials)

    def _make_one(self, name=None):
        client = self._make_credentials()
        return self._get_target_class()(client, name=name)


@click.command()
@click.option('--recursive', '-r', default=False, is_flag=True)
@click.argument('url')
@click.argument('dir')
def cp(recursive, url, dir):
    _parsedstr = url.replace('gs://', '').split('/', 1)
    bucket = TestClient()._make_one(name=_parsedstr[0])
    prefix = _parsedstr[1]

    return_blobs = [prefix]
    if prefix.endswith('_'):
        return_blobs = []
    if prefix.endswith('*'):
        return_blobs = ['1.txt', '2.txt']

    with mock.patch.object(bucket, 'list_blobs', return_value=return_blobs):
        blobs = bucket.list_blobs(prefix=prefix)

        if len(blobs) == 0:
            raise myutil.exceptions.CommandException('No URLs matched: {}'.format(url))
        if not recursive and len(blobs) > 1:
            print('Omitting prefix "gs://{}/{}/". (Did you mean to do cp -r?)'.format(bucket.name, prefix))
            raise myutil.exceptions.CommandException('No URLs matched')

    myutil.gcp.download_blobs(blobs=blobs, dir=dir, recursive=recursive)


def test_cp_missing_all_params():
    runner = CliRunner()
    result = runner.invoke(cp, [])
    assert result.exit_code == 2
    assert result.output == 'Usage: cp [OPTIONS] URL DIR\n\nError: Missing argument "url".\n'


def test_cp_missing_all_params_but_recursive():
    runner = CliRunner()
    result = runner.invoke(cp, ['-r'])
    assert result.exit_code == 2
    assert result.output == 'Usage: cp [OPTIONS] URL DIR\n\nError: Missing argument "url".\n'


def test_cp_missing_dir_param():
    runner = CliRunner()
    result = runner.invoke(cp, ['a'])
    assert result.exit_code == 2
    assert result.output == 'Usage: cp [OPTIONS] URL DIR\n\nError: Missing argument "dir".\n'


def test_cp_single_blob_recursive():
    with mock.patch('myutil.gcp.download_blobs') as download_blobs:
        runner = CliRunner()
        result = runner.invoke(cp, ['-r', 'gs://foo/a', 'b'])
        assert result.exit_code == 0
        assert result.output == ''
        download_blobs.assert_has_calls([call(blobs=['a'], dir='b', recursive=True)])


def test_cp_single_blob_nonrecursive():
    with mock.patch('myutil.gcp.download_blobs') as download_blobs:
        runner = CliRunner()
        result = runner.invoke(cp, ['gs://foo/a', 'b'])
        assert result.exit_code == 0
        assert result.output == ''
        download_blobs.assert_has_calls([call(blobs=['a'], dir='b', recursive=False)])


def test_cp_multiple_blobs_recursive():
    with mock.patch('myutil.gcp.download_blobs') as download_blobs:
        runner = CliRunner()
        result = runner.invoke(cp, ['-r', 'gs://foo/a/*', 'b'])
        assert result.exit_code == 0
        assert result.output == ''
        download_blobs.assert_has_calls([call(blobs=['1.txt', '2.txt'], dir='b', recursive=True)])


def test_cp_multiple_blobs_nonrecursive():
    with mock.patch('myutil.gcp.download_blobs') as download_blobs:
        runner = CliRunner()
        result = runner.invoke(cp, ['gs://foo/a/*', 'b'])
        assert result.exit_code == -1
        assert isinstance(result.exception, myutil.exceptions.CommandException)
        assert str(result.exception) == 'No URLs matched'
        assert result.output == 'Omitting prefix "gs://foo/a/*/". (Did you mean to do cp -r?)\n'
        assert not download_blobs.called


def test_cp_no_blobs_recursive():
    with mock.patch('myutil.gcp.download_blobs') as download_blobs:
        runner = CliRunner()
        result = runner.invoke(cp, ['-r', 'gs://foo/a/_', 'b'])
        assert result.exit_code == -1
        assert isinstance(result.exception, myutil.exceptions.CommandException)
        assert str(result.exception) == 'No URLs matched: gs://foo/a/_'
        assert result.output == ''
        assert not download_blobs.called


def test_cp_no_blobs_nonrecursive():
    with mock.patch('myutil.gcp.download_blobs') as download_blobs:
        runner = CliRunner()
        result = runner.invoke(cp, ['gs://foo/a/_', 'b'])
        assert result.exit_code == -1
        assert isinstance(result.exception, myutil.exceptions.CommandException)
        assert str(result.exception) == 'No URLs matched: gs://foo/a/_'
        assert result.output == ''
        assert not download_blobs.called
