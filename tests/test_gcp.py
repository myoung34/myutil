# -*- coding: utf-8 -*-
import google.auth.credentials
import google.cloud.storage.blob
import mock
import pytest
from mock import call

import myutil.exceptions
from myutil.gcp import download_blobs, tree_from_list


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


class TestBlob():

    @staticmethod
    def _make_one(*args, **kw):
        from google.cloud.storage.blob import Blob

        properties = kw.pop('properties', {})
        blob = Blob(*args, **kw)
        blob._properties.update(properties)
        return blob


def test_download_blob():
    bucket = TestClient()._make_one(name='bucket')
    blob = TestBlob()._make_one(bucket=bucket, name='1.txt')
    with mock.patch.object(blob, 'download_to_filename') as download_to_filename:
        myutil.gcp.download_blob(blob, '1.txt')
        download_to_filename.assert_has_calls([call('1.txt')])


def test_download_blob_to_dir_exists():
    bucket = TestClient()._make_one(name='bucket')
    blob = TestBlob()._make_one(bucket=bucket, name='/1.txt')
    with mock.patch('os.path.isdir', return_value=True):
        with mock.patch.object(blob, 'download_to_filename') as download_to_filename:
            myutil.gcp.download_blob(blob, 'asdf/')
            download_to_filename.assert_has_calls([call('asdf/1.txt')])


def test_download_blob_to_dir_dne():
    bucket = TestClient()._make_one(name='bucket')
    blob = TestBlob()._make_one(bucket=bucket, name='/')
    with pytest.raises(myutil.exceptions.CommandException):
        with mock.patch('os.path.isdir', return_value=False):
            with mock.patch.object(blob, 'download_to_filename') as download_to_filename:
                myutil.gcp.download_blob(blob, 'asdf/')
                assert not download_to_filename.called


def test_download_blobs_multiple_blobs_recursive_dir_dne():
    bucket = TestClient()._make_one(name='bucket')
    with pytest.raises(myutil.exceptions.CommandException):
        with mock.patch('myutil.gcp.mkdir_p') as mkdir_p:
            with mock.patch('os.path.isdir', return_value=False):
                with mock.patch('myutil.gcp.download_blob', return_value=None) as download_blob:
                    blobs = [
                        TestBlob()._make_one(bucket=bucket, name='a/1.txt'),
                        TestBlob()._make_one(bucket=bucket, name='a/b/2.txt'),
                    ]
                    download_blobs(blobs=blobs, dir='./localdir', recursive=True)
                    assert not download_blob.called
                    assert not mkdir_p.called


def test_download_blobs_multiple_blobs_recursive_dir_exists():
    bucket = TestClient()._make_one(name='bucket')
    with mock.patch('myutil.gcp.mkdir_p') as mkdir_p:
        with mock.patch('os.path.isdir', return_value=True):
            with mock.patch('myutil.gcp.download_blob', return_value=None) as download_blob:
                blobs = [
                    TestBlob()._make_one(bucket=bucket, name='a/1.txt'),
                    TestBlob()._make_one(bucket=bucket, name='a/b/2.txt'),
                ]
                download_blobs(blobs=blobs, dir='./localdir', recursive=True)
                download_blob.assert_has_calls([
                    call(blob=blobs[0], filename='./localdir/a/1.txt'),
                    call(blob=blobs[1], filename='./localdir/a/b/2.txt'),
                ])
                mkdir_p.assert_has_calls([
                    call('./localdir/a'),
                    call('./localdir/a/b'),
                ])


def test_download_blobs_single_blob_recursive_dir_dne():
    bucket = TestClient()._make_one(name='bucket')
    with mock.patch('myutil.gcp.mkdir_p') as mkdir_p:
        with mock.patch('os.path.isdir', return_value=False):
            with mock.patch('myutil.gcp.download_blob', return_value=None) as download_blob:
                blob = TestBlob()._make_one(bucket=bucket, name='1.txt')
                download_blobs(blobs=[blob], dir='./localdir', recursive=True)
                download_blob.assert_has_calls([call(blob=blob, filename='./localdir')])
                assert not mkdir_p.called


def test_download_blobs_single_blob_recursive_dir_exists():
    bucket = TestClient()._make_one(name='bucket')
    with mock.patch('myutil.gcp.mkdir_p') as mkdir_p:
        with mock.patch('os.path.isdir', return_value=True):
            with mock.patch('myutil.gcp.download_blob', return_value=None) as download_blob:
                blob = TestBlob()._make_one(bucket=bucket, name='1.txt')
                download_blobs(blobs=[blob], dir='./localdir', recursive=True)
                download_blob.assert_has_calls([call(blob=blob, filename='./localdir')])
                assert not mkdir_p.called


def test_download_blobs_multiple_blobs_nonrecursive_dir_dne():
    bucket = TestClient()._make_one(name='bucket')
    with pytest.raises(myutil.exceptions.CommandException):
        with mock.patch('myutil.gcp.mkdir_p') as mkdir_p:
            with mock.patch('os.path.isdir', return_value=False):
                with mock.patch('myutil.gcp.download_blob', return_value=None) as download_blob:
                    blobs = [
                        TestBlob()._make_one(bucket=bucket, name='a/1.txt'),
                        TestBlob()._make_one(bucket=bucket, name='a/b/2.txt'),
                    ]
                    download_blobs(blobs=blobs, dir='./localdir', recursive=False)
                    assert not download_blob.called
                    assert not mkdir_p.called


def test_download_blobs_multiple_blobs_nonrecursive_dir_exists():
    bucket = TestClient()._make_one(name='bucket')
    with mock.patch('myutil.gcp.mkdir_p') as mkdir_p:
        with mock.patch('os.path.isdir', return_value=True):
            with mock.patch('myutil.gcp.download_blob', return_value=None) as download_blob:
                blobs = [
                    TestBlob()._make_one(bucket=bucket, name='1.txt'),
                    TestBlob()._make_one(bucket=bucket, name='2.txt'),
                ]
                download_blobs(blobs=blobs, dir='./localdir', recursive=False)
                download_blob.assert_has_calls([
                    call(blob=blobs[0], filename='./localdir/1.txt'),
                    call(blob=blobs[1], filename='./localdir/2.txt'),
                ])
                mkdir_p.assert_has_calls([
                    call('./localdir'),
                    call('./localdir'),
                ])


def test_download_blobs_single_blob_nonrecursive_dir_dne():
    bucket = TestClient()._make_one(name='bucket')
    with mock.patch('myutil.gcp.mkdir_p') as mkdir_p:
        with mock.patch('os.path.isdir', return_value=False):
            with mock.patch('myutil.gcp.download_blob', return_value=None) as download_blob:
                blob = TestBlob()._make_one(bucket=bucket, name='1.txt')
                download_blobs(blobs=[blob], dir='./localdir', recursive=False)
                download_blob.assert_has_calls([call(blob=blob, filename='./localdir')])
                assert not mkdir_p.called


def test_download_blobs_single_blob_nonrecursive_dir_exists():
    bucket = TestClient()._make_one(name='bucket')
    with mock.patch('myutil.gcp.mkdir_p') as mkdir_p:
        with mock.patch('os.path.isdir', return_value=True):
            with mock.patch('myutil.gcp.download_blob', return_value=None) as download_blob:
                blob = TestBlob()._make_one(bucket=bucket, name='1.txt')
                download_blobs(blobs=[blob], dir='./localdir', recursive=False)
                download_blob.assert_has_calls([call(blob=blob, filename='./localdir')])
                assert not mkdir_p.called


def test_tree_from_list():
    bucket = TestClient()._make_one(name='bucket')
    blob = TestBlob()._make_one(bucket=bucket, name='1.txt')
    root_node = tree_from_list(blobs=[blob])
    assert root_node.name == '/'
    assert root_node.children[0].name == '1.txt'
    assert len(root_node.children) == 1
    assert root_node.depth == 0
