"""
PIL wrapper
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six

import numpy as np

try:
    from PIL import Image, PngImagePlugin
except ImportError:
    import Image
    import PngImagePlugin


def read_png_float(file):
    """
    Read in a PNG file, converting values to floating-point doubles
    in the range (0, 1)

    Parameters
    ----------
    file : str path or file-like object
    """
    data = read_png_int(file)
    norm = 2 ** (data.itemsize * 8) - 1
    return data.astype(dtype=np.float, copy=False) / norm


def read_png_int(file):
    """
    Read in a PNG file with original integer values.

    Parameters
    ----------
    file : str path or file-like object
    """
    im = Image.open(file)
    rawmode = im.png.im_rawmode
    print('***', 'openmode', im.mode, rawmode)
    b16 = im.png.im_rawmode.endswith(';16B')
    #if im.png.im_rawmode.endswith(';16B'):
    #    im.mode = im.png.im_rawmode
    if 'transparency' in im.info:
        im = im.convert('RGBA;16B' if b16 else 'RGBA')
    elif im.mode.split(';', 1)[0] not in ['1', 'L', 'I', 'RGB', 'RGBA']:
    #elif im.mode.split(';', 1)[0] not in ['I', 'RGB', 'RGBA']:
        im = im.convert('RGB;16B' if b16 else 'RGB')
    # TODO: F-mode
    #if im.png.im_rawmode == 'I;16B':
    #    im = im.convert(im.png.im_rawmode)
    print('***', 'workmode', im.mode, rawmode)
    if im.mode == '1':
        buffer = np.array(im, dtype=np.bool_)
    elif b16:
        buffer = np.array(im, dtype=np.uint16)
    else:
        buffer = np.array(im, dtype=np.uint8)
    print('>>> shape', buffer.shape)
    #if buffer.ndim == 2:
    #    buffer = buffer[:, :, np.newaxis]
    #    print('reshaped', buffer.shape)
    return buffer


def read_png(file):
    """
    Read in a PNG file, converting values to floating-point doubles
    in the range (0, 1)

    Alias for read_png_float()

    Parameters
    ----------
    file : str path or file-like object
    """
    return read_png_float(file)


def write_png(buffer, file, dpi=None, compress_level=6, optimize=None, metadata=None):
    """
    Parameters
    ----------
    buffer : numpy array of image data
        Must be an MxNxD array of dtype uint8.
        - If D is 1, the image is greyscale
        - If D is 3, the image is RGB
        - If D is 4, the image is RGBA

    file : str path, file-like object or None
        - If a str, must be a file path
        - If a file-like object, must write bytes
        - If None, a byte string containing the PNG data will be returned

    dpi : float
        The dpi to store in the file metadata.

    compress_level : int
        ZLIB compression level, a number between 0 and 9: 1 gives best speed,
        9 gives best compression, 0 gives no compression at all. Default is 6.
        When `optimize` option is True `compress_level` has no effect
        (it is set to 9 regardless of a value passed).

    optimize : bool
        If present, instructs the PNG writer to make the output file as small
        as possible. This includes extra processing in order to find optimal
        encoder settings.

    metadata : dictionary
        The keyword-text pairs that are stored as comments in the image.
        Keys must be shorter than 79 chars. The only supported encoding
        for both keywords and values is Latin-1 (ISO 8859-1).
        Examples given in the PNG Specification are:
        - Title: Short (one line) title or caption for image
        - Author: Name of image's creator
        - Description: Description of image (possibly long)
        - Copyright: Copyright notice
        - Creation Time: Time of original image creation
                         (usually RFC 1123 format, see below)
        - Software: Software used to create the image
        - Disclaimer: Legal disclaimer
        - Warning: Warning of nature of content
        - Source: Device used to create the image
        - Comment: Miscellaneous comment; conversion
                   from other image format

    Returns
    -------
    buffer : bytes or None
        Byte string containing the PNG content if None was passed in for
        file, otherwise None is returned.
    """
    # https://pillow.readthedocs.io/en/3.0.x/PIL.html#PIL.PngImagePlugin.PngInfo
    info = PngImagePlugin.PngInfo()
    if metadata:
        for key, value in six.iteritems(metadata):
            info.add_text(key, value)

    # TODO: RendererAgg needs support of array interface
    #buffer = np.ascontiguousarray(buffer)
    #buffer = np.frombuffer(buffer)
    buffer = np.asarray(buffer)
    # PIL does not like (w, h, 1) shape
    #buffer = buffer.squeeze()
    if buffer.ndim == 3 and buffer.shape[2] == 1:
        buffer = buffer.reshape(buffer.shape[:2])
    #print('save', '>', buffer.shape, '<')
    #im = Image.fromarray(buffer)
    if buffer.ndim == 3:
        mode = {1: 'L', 3: 'RGB', 4: 'RGBA'}[buffer.shape[2]]
    elif buffer.ndim == 2:
        mode = 'I'
    else:
        raise ValueError("Unsupported input buffer dimension")
    if buffer.itemsize == 2:
        mode += ';16'
    elif buffer.itemsize > 2:
        raise ValueError("Unsupported input buffer dtype")
    # TODO: support float
    print('*** savemode', mode)
    im = Image.fromarray(buffer, mode=mode)

    if dpi is not None:
        dpi = dpi, dpi
    # https://pillow.readthedocs.io/en/3.0.x/handbook/image-file-formats.html#png
    params = dict(dpi=dpi, compress_level=compress_level,
                  optimize=optimize, pnginfo=info)
    # https://pillow.readthedocs.io/en/3.0.x/reference/Image.html#PIL.Image.Image.save
    im.save(file, format='png', **params)
    # TODO: support file is None
