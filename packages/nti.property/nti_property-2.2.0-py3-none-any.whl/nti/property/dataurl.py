#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Objects for working with the RFC2397 ``data`` URL scheme::

    data:[<MIME-type>][;charset=<encoding>][;base64],<data>

The encoding is indicated by ``;base64``. If it's present the data is
encoded as base64. Without it the data (as a sequence of octets) is
represented using ASCII encoding for octets inside the range of safe
URL characters and using the standard %xx hex encoding of URLs for
octets outside that range. If ``<MIME-type>`` is omitted, it defaults
to ``text/plain;charset=US-ASCII``. (As a shorthand, the type can be
omitted but the charset parameter supplied.)

"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

try:
    from urllib.parse import quote
    from urllib.parse import unquote
except ImportError: # pragma: no cover
    # Python 2
    from urllib import quote
    from urllib import unquote

from base64 import b64decode
from base64 import b64encode

from zope.cachedescriptors.property import CachedProperty

# Originally inspired by
# http://code.google.com/p/python-mom/source/browse/mom/net/scheme/dataurl.py?


def decode(data_url):
    """
    Decodes a data URL into raw bytes and metadata.

    :param data_url: The data url string.
       If a mime-type definition is missing in the metadata,
       ``text/plain;charset=US-ASCII`` will be used as default mime-type.
    :returns: A 2-tuple: ``(bytes, mime_type_string)``
       The mime_type string will not be parsed. See :func:`zope.contenttype.parse.parse` for that.
    """

    if isinstance(data_url, DataURL):
        return data_url.data, data_url.mimeType
    return _do_decode(data_url)


def _do_decode(data_url):
    metadata, encoded = data_url.rsplit(",", 1)
    _, metadata = metadata.split("data:", 1)
    metadata_parts = metadata.rsplit(";", 1)
    if metadata_parts[-1] == "base64":
        _decode = b64decode
        metadata_parts = metadata_parts[:-1]
    else:
        _decode = unquote
    if not metadata_parts or not metadata_parts[0]:
        metadata_parts = ("text/plain;charset=US-ASCII",)
    mime_type = metadata_parts[0]
    raw_bytes = _decode(encoded)
    return raw_bytes, mime_type


class DataURL(str):  # native string on both py2 and py3
    """
    Represents a data URL with convenient access
    to its raw bytes and mime type.
    """

    @CachedProperty
    def _decoded(self):
        return _do_decode(self)

    @property
    def data(self):
        return self._decoded[0]

    @property
    def mimeType(self):
        return self._decoded[1]

_def_charset = 'US-ASCII'
_marker = object()


def encode(raw_bytes,
           mime_type='text/plain',
           charset=_marker,
           encoder="base64"):
    """
    Encodes raw bytes into a data URL scheme string.

    :param raw_bytes: Raw bytes
    :param mime_type: The mime type, e.g.
         ``b"text/css"`` or ``b"image/png"``. Default ``b"text/plain"``.
    :param charset: Set to ``b"utf-8"`` if you want the data URL to contain a ``b"charset=utf-8"``
            component. Default ``b'US-ASCII'``. This does not mean however, that your
            raw_bytes will be encoded by this function. You must ensure that
            if you specify, ``b"utf-8"`` (or anything else) as the encoding, you
            have encoded your raw data appropriately.

            .. note:: This function employs a heuristic to know when to default this
                    parameter (for example, it is not used for image mime types). To be absolutely
                    sure, set it explicitly (None always meaning not to use it).
    :param encoder: The string "base64" (the default) or None. If None, the data
            is directly output as quoted ASCII bytes.
    :returns: Data URL byte string
    """
    if not isinstance(raw_bytes, bytes): # pragma: no cover
        raise TypeError("only raw bytes can be encoded")

    if encoder == "base64":
        _encode = b64encode
        codec = ";base64,"
    else:
        # We want ASCII bytes.
        def _encode(data):
            return quote(data).encode('ascii')
        codec = ","
    mime_type = mime_type or ""

    if charset is _marker:
        if mime_type.startswith('text/'):
            charset = _def_charset
        else:
            charset = None

    charset = ";charset=" + charset if charset else ""
    encoded = _encode(raw_bytes)
    if isinstance(encoded, bytes):
        encoded = encoded.decode("utf-8") # pylint:disable=redefined-variable-type
    return ''.join(("data:", mime_type, charset, codec, encoded))
