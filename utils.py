import re
from PIL import Image
import numpy as np

import os


def to_fname(name, ext):
    '''
    Function for converting a president's name into a file name

    Parameters
    ----------
    name: name of president
    ext: extension of file (i.e. .jpg or .txt)
    '''

    return "_".join(re.sub(r"\.", "", name.lower()).split(" ")) + ext


def to_url(name):
    '''
    Function for converting a president's name into a Wikipedia URL

    Parameters
    ----------
    name: name of president
    '''

    name = "_".join(name.split(" "))
    return "https://en.wikipedia.org/wiki/{}".format(name)


def clean_extra_spaces(string):
    '''
    Function cleaning all extra spaces from a string

    Parameters
    ----------
    string: string to clean extra spaces from
    '''

    return re.sub("(\s\s)+", "", string).strip()


def extract_dates(string):
    '''
    Function for extracting dates from a string

    Parameters
    ----------
    string: string containing dates in the long format (i.e. January 1, 2020)
    '''

    return re.findall("([A-Za-z]+\s\d+,\s\d{4})", string)


def resize(image_path, save_path, target_height=220):
    '''
    Function for resizing an image by shrinking the height (for getting uniform presidential portraits)

    Parameters
    ----------
    image_path: file path to image
    save_path: file path to save edited image
    target_height: height in pixels that you want the resulting picture to be (default 220 px)
    '''

    im = Image.open(image_path)
    arr = np.array(im)
    height = arr.shape[0]
    width = arr.shape[1]
    over = height - target_height

    counter = 0

    while counter < over:
        arr = np.delete(arr, arr.shape[0] - 1, 0)
        counter += 1

    resized_im = Image.fromarray(arr)
    resized_im.save(save_path)
