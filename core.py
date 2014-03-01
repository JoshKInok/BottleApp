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

class FileInfo(dict):
    "store file metadata"

    def __init__(self, filename=None):
        _filename = os.path.basename(filename)
        try:
            _title = images_and_titles[_filename]
        except:
            _title = "No Title"
        self[_filename] = _title


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
def index():
    return template('index',
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


def mylistDir(directory, fileExtList):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for extensions in fileExtList:
            for filename in fnmatch.filter(filenames, extensions):
                matches.append(filename)
    return matches

def _glob(path, *exts):
    """Glob for multiple file extensions

    Parameters
    ----------
    path : str
        A file name without extension, or directory name
    exts : tuple
        File extensions to glob for

    Returns
    -------
    files : list
        list of files matching extensions in exts in path

    """
    path = os.path.join(path, "*") if os.path.isdir(path) else path + "*"
    return [os.path.basename(f) for files in [glob.glob(path + ext) for ext in exts] for f in files]

    
if __name__ == "__main__":
    # INITIALIZE
    #extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif']
    extensions = '.jpg', '.jpeg', '.png', '.gif'
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

    # Build the list of images
    ## image_list = mylistDir(the_dir, extensions)
    #image_list = _glob(the_dir, str(extensions))
    image_list = _glob(the_dir, '.jpg', '.jpeg', '.png', '.gif')

    print('image_list count: {0:n}'.format(len(image_list)))
    #image_dict = listDirectory(the_dir, extensions)

    if not image_list:
        raise EmptyDirException

    logger.info('shuffling')
    random.shuffle(image_list)
    #logger.debug('image_list:{0:s}'.format(image_list))
    #logger.debug('image_dict:{0:s}'.format(image_dict))
    #logger.debug('images_and_titles:{0:s}'.format(images_and_titles))


# added this just to see if it syncs
    bottle.debug()
    try:
        bottle.run(host='0.0.0.0', port=8889) # , quiet=True
    except socket.error, e:
        raise
