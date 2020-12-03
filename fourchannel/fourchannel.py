import sys, json, os
import urllib.request
import urllib.parse
import argparse
import time
import signal
import re

# wishlist
#
# - get thread number of latest jav or gravure
# - use threads to download in parallel


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
max_retry = 1
resorted_to_archive = False
hit_cloudflare_block = False

def fuuka_retrieve(result, board, thread, dryrun):
    i = 0
    global hit_cloudflare_block
    for post in result[thread]['posts']:
        if result[thread]['posts'][post]['media'] is None:
            continue
        filename = result[thread]['posts'][post]['media']['media_orig']
        if filename[filename.index('.'):] in allowed_types and not os.path.exists(filename):
            if not dryrun:
                # retrieve file from warosu.org, https://i.warosu.org/data/<board>/img/0xxx/xx/<filename>
                thread_first_3nums = '0' + thread[:3]
                thread_forth_and_fifth_nums = thread[3:5]
                url_warosu = 'https://i.warosu.org/data/' + board + '/img/' + thread_first_3nums + '/' + thread_forth_and_fifth_nums + '/' + filename

                if not hit_cloudflare_block:
                  print(f"downloading {filename}")
                  req = urllib.request.Request(url_warosu, headers={'User-Agent': 'Mozilla/5.0'})
                  try:
                    response = urllib.request.urlopen(req)
                    with open(filename, "wb") as file:
                      file.write(response.read())
                  except urllib.error.HTTPError as e:
                      if e.code in [503] and e.hdrs['Server'] == 'cloudflare':
                        hit_cloudflare_block = True
                        print(f"hit cloudflare block: {e}")
                else:
                    print(f"cloudflare block, download {url_warosu} manually in the browser")

                i = i+1
            else:
                print(f"skipping {filename}, dryrun")
        else:
            if not watching:
                print(f"skipping {filename}, already present")
    print(f"downloaded {i} files from {url_warosu}")


# loops through posts of given thread and downloads media files
def load_thread_json(board, thread, url, recurse, dryrun=False):
    global resorted_to_archive
    response = None
    archive_url_is_being_used_for_this_stack_frame_so_call_fuuka = False
    try:
      if resorted_to_archive is True:
        archive_url_is_being_used_for_this_stack_frame_so_call_fuuka = True
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
      else:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
      if e.code in [404]:
          if not resorted_to_archive:
            print(f"url {url} returned 404, resorting to https://archived.moe/")
            resorted_to_archive = True
            newurl = '%s=%s&num=%s' % ('https://archived.moe/_/api/chan/thread?board', board, thread)
            load_thread_json(board, thread, newurl, recurse-1, dryrun)
          else:
            global max_retry
            max_retry = max_retry - 1
            if max_retry < 1:
                return
            else:
                print(f"archive url {url} returned 404, retrying...")
                load_thread_json(board, thread, newurl, recurse, dryrun)
      else:
        print(f"unhandled error: {e}")
        return

    try:
        result = json.loads(response.read())
        if recurse > 0:
          try:
            prev_thread_path = re.search(r'^.*Previous thread.*href="([^"]+)".*$', result['posts'][0]['com']).group(1)
            split = urllib.parse.urlparse('https://boards.4channel.org' + prev_thread_path).path.replace('/', ' ').split()
            newurl = '%s%s/thread/%s.json' % (URL, split[0], split[2])
            print(f"recursing to {prev_thread_path}")
            load_thread_json(board, split[2], newurl, recurse-1, dryrun)
          except AttributeError:
              pass

        if archive_url_is_being_used_for_this_stack_frame_so_call_fuuka is True:
          fuuka_retrieve(result, board, thread, dryrun)
        else:
            i = 0
            for post in result['posts']:
                try:
                    filename = str(post['tim']) + post['ext']
                    if post['ext'] in allowed_types and not os.path.exists(filename):
                        if not dryrun:
                            print(f"downloading {filename}")
                            urllib.request.urlretrieve(IMAGE_URL + board + '/' + filename, filename)
                            i = i+1
                        else:
                            print(f"skipping {filename}, dryrun")
                    else:
                        if not watching:
                            print(f"skipping {filename}, already present")
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
    outdir = kwargs.get('out') if kwargs.get('out') is not None else thread

    try:
        os.mkdir(outdir)
        print(f"created {os.path.join(os.getcwd(), outdir)} directory...")
    except OSError:
        print(f"{outdir} directory already exists, continuing...")
        pass

    if os.path.basename(os.getcwd()) != outdir:
        os.chdir(outdir)

    if kwargs.get('webm') is True:
        allowed_types.append('.webm')
    
    if kwargs.get('watch') is True:
      global watching
      watching = True
      print(f"watching /{board}/{thread} for new images")
      while True:
        load_thread_json(board, thread, url, 0)
        time.sleep(60)
    else:
      print(f"downloading /{board}/{thread}")
      load_thread_json(board, thread, url, kwargs.get('recurse'), kwargs.get('dryrun'))
    
    os.chdir("..")


def signal_handler(signal, frame):
    print('\nSIGINT or CTRL-C detected, exiting gracefully')
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help='the url of the thread.')
    parser.add_argument("out", nargs='?', help='specify output directory (optional)')
    parser.add_argument("--webm", action="store_true", help="in addition to images also download webm videos.")
    parser.add_argument("--watch", action='store_true', help='watch the thread every 60 seconds for new images.')
    parser.add_argument("--dryrun", action="store_true", help="dry run without actually downloading images.")
    parser.add_argument('-r', "--recurse", type=int, default=0, help="recursively download images if 1st post contains link to previous thread up to specified depth")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    download(**vars(args)) # pass in args as dict and unpack


if __name__ == '__main__':
    main()
