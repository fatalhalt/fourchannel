import sys, json, os
import urllib.request
import urllib.parse
import argparse
import time

"""
  notes:
    - for module to be importable, it is good idea not to do ArgumentParser in global scope
    - to avoid typing 'import fourchannel.fourchannel' and then 'fourchannel.fourchannel.download'
      'from .fourchannel import download' was added to __init__.py
"""

URL = 'https://a.4cdn.org/'
IMAGE_URL = 'https://i.4cdn.org/'
allowed_types = ['.jpg', '.png', '.gif']


def load_thread_json(board, url, dryrun=False):
    response = urllib.request.urlopen(url)
    try:
        result = json.loads(response.read())
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
                    print(f"skipping {filename}")
            except KeyError:
                continue
        print(f"downloaded {i} files")
    except ValueError:
        sys.exit('no response, thread deleted?')


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
    print(f"downloading /{board}/{thread}")
    load_thread_json(board, url)
    os.chdir("..")


def watch(board, url):
    while True:
        load_thread_json(board, url)
        time.sleep(60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help='The url of the thread.')
    parser.add_argument("--webm", action="store_true", help="in addition to images also download webm videos.")
    parser.add_argument("--watch", action='store_true', help='If this argument is passed, we will watch the thread for new images.')
    parser.add_argument("--dryrun", action="store_true", help="dry run without actually downloading images.")
    args = parser.parse_args()

    if args.watch:
        print(f"watching /{board}/{thread} for new images")
        watch(board, url)
    else:
        download(**vars(args)) # pass in args as dict and unpack


if __name__ == '__main__':
    main()
