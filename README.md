
4channel is a python3 tool and module to download all images/webm from a 4channel thread.

Installation
---------------

### Dependencies

4channel requires:
 
 - python (>= 3.6)

### User installation

```
pip install 4channel
```

Usage
---------

```
usage: 4channel [-h] [--webm] [--watch] [--dryrun] [--recurse] url

positional arguments:
  url         The url of the thread.

optional arguments:
  -h, --help  show this help message and exit
  --webm      in addition to images also download webm videos.
  --watch     If this argument is passed, we will watch the thread for new images.
  --dryrun    dry run without actually downloading images.

examples:
  python -m fourchannel https://boards.4channel.org/g/thread/76759434#p76759434

  import fourchannel as f
  f.download(url='https://boards.4channel.org/g/thread/76759434#p76759434')
```
