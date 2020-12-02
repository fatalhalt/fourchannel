import sys, json, os
import urllib.request
import urllib.parse
import argparse
import time
import signal
import re

"""
  notes:
    - for module to be importable, it is good idea not to do ArgumentParser in global scope
    - to avoid typing 'import fourchannel.fourchannel' and then 'fourchannel.fourchannel.download'
      'from .fourchannel import download' was added to __init__.py
"""

URL = 'https://a.4cdn.org/'
IMAGE_URL = 'https://i.4cdn.org/'
allowed_types = ['.jpg', '.png', '.gif']
watching = False


# loops through posts of given thread and downloads media files
def load_thread_json(board, url, dryrun=False, recurse=False):
    try:
      response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
      if e.code in [404]:
          return

    try:
        result = json.loads(response.read())
        if recurse:
          try:
            prev_thread_path = re.search(r'^.*Previous thread.*href="([^"]+)".*$', result['posts'][0]['com']).group(1)
            split = urllib.parse.urlparse('https://boards.4channel.org' + prev_thread_path).path.replace('/', ' ').split()
            newurl = '%s%s/thread/%s.json' % (URL, split[0], split[2])
            print(f"recursing to {prev_thread_path}")
            load_thread_json(board, newurl, dryrun, True)
          except AttributeError:
              pass

        i = 0
        for post in result['posts']:
            try:
                filename = str(post['tim']) + post['ext']
                if post['ext'] in allowed_types and not os.path.exists(filename):
                    print(f"downloading {filename}")
                    if not dryrun:
                        urllib.request.urlretrieve(IMAGE_URL + board + '/' + filename, filename)
                        i = i+1
                else:
                    if not watching:
                        print(f"skipping {filename}")
            except KeyError:
                continue
        print(f"downloaded {i} files from {url}")
    except ValueError:
        sys.exit('no response, thread deleted?')


# the key function that that we expect to be used when 4channel is imported as a module
# this function parses user's URL and calls load_thread_json() that does the actual downloading
def download(**kwargs):
    if 'boards.4channel.org' not in kwargs.get('url'):
        sys.exit("you didn't enter a valid 4channel URL")

    split = urllib.parse.urlparse(kwargs.get('url')).path.replace('/', ' ').split()
    board, thread = split[0], split[2]
    url = '%s%s/thread/%s.json' % (URL, board, thread)

    try:
        os.mkdir(thread)
        print(f"created {os.path.join(os.getcwd(), thread)} directory...")
    except OSError:
        print(f"{thread} directory already exists, continuing...")
        pass

    if os.path.basename(os.getcwd()) != thread:
        os.chdir(thread)

    if kwargs.get('webm') is True:
        allowed_types.append('.webm')
    
    if kwargs.get('watch') is True:
      global watching
      watching = True
      print(f"watching /{board}/{thread} for new images")
      while True:
        load_thread_json(board, url)
        time.sleep(60)
    else:
      print(f"downloading /{board}/{thread}")
      load_thread_json(board, url, kwargs.get('dryrun'), kwargs.get('recurse'))
    
    os.chdir("..")


def signal_handler(signal, frame):
    print('\nSIGINT or CTRL-C detected, exiting gracefully')
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help='The url of the thread.')
    parser.add_argument("--webm", action="store_true", help="in addition to images also download webm videos.")
    parser.add_argument("--watch", action='store_true', help='watch the thread every 60 seconds for new images.')
    parser.add_argument("--dryrun", action="store_true", help="dry run without actually downloading images.")
    parser.add_argument("--recurse", action="store_true", help="recursively download images if 1st post contains link to previous thread")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    download(**vars(args)) # pass in args as dict and unpack


if __name__ == '__main__':
    main()
