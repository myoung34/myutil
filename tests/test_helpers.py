# -*- coding: utf-8 -*-
import pytest

from myutil.helpers import bucket_path_from_url


def test_bucket_path_from_url_invalid_url():
    with pytest.raises(Exception):
        bucket_path_from_url('foo')


def test_bucket_path_from_url_no_url():
    with pytest.raises(Exception):
        bucket_path_from_url('gs://')


def test_bucket_path_from_url():
    output = bucket_path_from_url('gs://foo/a')
    assert output == ('foo', 'a')
