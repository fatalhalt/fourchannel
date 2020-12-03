
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
usage: 4channel.py [-h] [--webm] [--watch] [--dryrun] [-r RECURSE] url [out]

positional arguments:
  url                   the url of the thread.
  out                   specify output directory (optional)

optional arguments:
  -h, --help            show this help message and exit
  --webm                in addition to images also download webm videos.
  --watch               watch the thread every 60 seconds for new images.
  --dryrun              dry run without actually downloading images.
  -r RECURSE, --recurse RECURSE
                        recursively download images if 1st post contains link to previous thread up to specified depth
examples:
  python -m fourchannel https://boards.4channel.org/g/thread/76759434#p76759434

  import fourchannel as f
  f.download(url='https://boards.4channel.org/g/thread/76759434#p76759434')
```
