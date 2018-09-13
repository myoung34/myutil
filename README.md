MYutil (Marcus Young gsutil)
============================

![](https://travis-ci.org/myoung34/myutil.svg?branch=master)

Just a basic re-implementation of some of the [gsutil](https://cloud.google.com/storage/docs/gsutil) commands.


# Install

 * `make install`
 * `python setup.py install`

# Tests

```bash
$ pipenv install
$ pipenv shell
$ pytest test/
```

# Usage

```
$ myutil
Usage: myutil [OPTIONS] COMMAND [ARGS]...

  Grouping mechanism

Options:
  --help  Show this message and exit.

Commands:
  cp  Copy blobs from a bucket Keyword arguments:...
  ls  List objects in a bucket Keyword arguments:...
```

### Pretty list a bucket

```
$ myutil ls gs://somebucket/

└── mydir
    └── a
        ├── 1.txt
        └── b
            └── 2.txt
```

### Copy a file locally

```
$ myutil cp -r gs://somebucket/mydir/a/1.txt .
Copying gs://somebucket/mydir/a/1.txt...

```

### Copy a file locally (recursive)

```
$ myutil cp -r gs://somebucket/mydir .
Copying gs://somebucket/mydir/a/1.txt...
Copying gs://somebucket/mydir/a/b/2.txt...
```
