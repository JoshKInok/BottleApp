import os
import sys
import re
import logging
from argparse import ArgumentParser
from collections import defaultdict, Counter
import pickle
import fnmatch
import random
import glob

from bottle import template, request, static_file, redirect, post, get
import bottle


class EmptyDatFileException(Exception):
    """Exception raised when the directory does not have a data.dat"""


class EmptyDirException(Exception):
    """Exception raised when Dir contains  no images"""

SCRIPT_DIR = sys.path[0]


# STATIC ROUTES
@get('/static/<filepath:path>')
def server_static(filepath):
    """serves css and js
    """
    return static_file(filepath, root=os.path.join(SCRIPT_DIR, 'static'))


@get('/image/<imagepath:path>')
def server_static(imagepath):
    """serves the images in the directory passed to it
    """
    return static_file(imagepath, root=the_dir)


@get('/thumbs/<thumbpath:path>')
def server_static(thumbpath):
    """ serves the thumbs
    """
    return static_file(thumbpath, root=os.path.join(the_dir, 'thumbs'))

@get('/favicon.ico')
def get_favicon():
    return static_file('favicon.ico', root=SCRIPT_DIR+"/static")


@get('/')
def main_page():
    return template('main', options=list_directories(the_dir))

@post('/index')
@get('/index')
def index():
    page_to_use = request.POST.get('selector')
    print('will use {0:s}'.format(page_to_use))
    new_dir = os.path.join(the_dir,page_to_use)
    image_list = mylistDir(new_dir, extensions)
    #image_list = _glob(os.path.join(the_dir, page_to_use), '.jpg', '.jpeg', '.png', '.gif')
    return template('index',
                    root_dir=page_to_use,
                    image_list=image_list,
                    images_and_titles=images_and_titles,
                    page_title=os.path.basename(the_dir)
    )


def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create a file handler for DEBUG
    log_file = os.path.join(SCRIPT_DIR, 'hello.log')
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    # create a console logger to get INFO
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create a log formatter and add to handlers
    formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # add the handlers to the logger
    logger.info('Started logging to : {0:s}'.format(log_file))
    logger.debug('{0:s}Started{0:s}'.format('*' * 30))
    return logger


def init_parser():
    parser = ArgumentParser(description='Doing something')
    parser.add_argument('dir', metavar='<dir>', help='Directory to filter.')
    parser.add_argument('-exts', metavar='<exts>', help='Additional extension wanted.',
                        nargs='+')
    return parser


def listDirectory(directory, fileExtList):
    "get list of file info objects for files of particular extensions"
    fileList = [os.path.normcase(f) for f in os.listdir(directory)]
    fileList = [os.path.join(directory, f) for f in fileList \
                if os.path.splitext(f)[1] in fileExtList]
    def getFileInfoClass(filename, module=sys.modules[FileInfo.__module__]):
        "get file info class from filename extension"
        subclass = "%sFileInfo" % os.path.splitext(filename)[1].upper()[1:]
        return hasattr(module, subclass) and getattr(module, subclass) or FileInfo
        #return FileInfo
    return [getFileInfoClass(f)(f) for f in fileList]


def is_image_file(filename, extensions=['.jpg', '.jpeg', '.gif', '.png']):
    return any(filename.endswith(e) for e in extensions)


def mylistDir(directory, fileExtList):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filter(is_image_file, filenames):
            matches.append(filename)
    return matches


def list_directories(path):
    f = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f.extend(dirnames)
        break
    return sorted(f, key=str.lower)


if __name__ == "__main__":
    # INITIALIZE
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']
    parser = init_parser()
    logger = init_logger()

    # parse the args and log it
    args = parser.parse_args()
    the_dir = args.dir
    the_dir = os.path.abspath(the_dir)
    if args.exts:
        extensions.extend(args.exts)
    logger.info('will check for: {0:s}'.format(extensions))
    logger.info('listing dir: {0:s}'.format(the_dir))

    data_path = os.path.join(os.path.abspath(the_dir), 'data.dat')

    logger.info('opening: %s' % data_path)

    try:
        images_and_titles = open(data_path, 'rb')
    except IOError:
        logger.warning('no file: {0:s}'.format(data_path))

    try:
        images_and_titles = pickle.load(images_and_titles)
    except Exception as e:
        logger.warning('There will be no titles {0:s}'.format(e))
        images_and_titles = {}

    bottle.debug()
    try:
        bottle.run(host='0.0.0.0', port=8889) # , quiet=True
    except socket.error, e:
        raise
