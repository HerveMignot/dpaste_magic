# dpaste magic command
#
# Author: HerveMignot
# November 2018

"""
Magic function that push or pull code snippets out of dpaste.

%dpaste answer = 42
returns a dpaste.de url for line.

%%dpaste
answer = 42
returns a dpaste url for cell.

%dpaste or %%dpaste {-1x -1h -1d -1w -0}
post with expires duration (-1x for one time/two views, -0 is forever).

%dpaste -g WXYZ
answer = 42
retrieves snippet from WXYZ url hash.

%getdpaste WXYZ
answer = 42
retrieves snippet from WXYZ url hash.

%dpaste -g https://dpaste.de/WXYZ
answer = 42
retrieves snippet from dpaste.de url (with or without /raw).

%dpaste -u -g https://dpaste.de/WXYZ
# https://dpaste.de/WXYZ/raw

answer = 42
retrieves snippet from dpaste.de url (with or without /raw).

%getdpaste https://dpaste.de/WXYZ
answer = 42
retrieves snippet from dpaste.de url (with or without /raw).

%getdpaste -u https://dpaste.de/WXYZ
# https://dpaste.de/WXYZ/raw

answer = 42
retrieves snippet from dpaste.de url (with or without /raw).

"""
from __future__ import print_function

import logging
import sys
import getopt
import requests

from html.parser import HTMLParser

#from contextlib import redirect_stdout
from IPython import get_ipython
from IPython.core.magic import register_line_cell_magic, register_line_magic
from IPython.core.error import UsageError


# API supported durations, but currently some are not available with dpaste.de
# _durations = {
#     'x': 'onetime', 'h': '3600', 'd': '86000', 'w': '604800', '0': 'never',
# }

# dpaste.de currently supported duration for expires
_durations = {
    'x': 'onetime', 'h': '3600', 'd': '86000', 'w': '604800',
}
DEFAULT_DURATION = 'h'
_DURATION_OPTIONS = '1:g:uos' # '01:g:os' with never

_GETDPASTE_OPTIONS = 'u'

# DPASTE.DE URLs
DPASTE_DE_URL = 'https://dpaste.de/'
DPASTE_DE_API = 'https://dpaste.de/api/'
GET_DPASTE_DE_URL = 'https://dpaste.de/{}/raw'


def _post_to_dpaste(content, expires='3600', format='URL'):
    """
    Post a content to dpaste.de with expiration and return code & URL
    """
    try:
        r = requests.post(DPASTE_DE_API,
                          data={
                              'content': content,
                              'format': format,
                              'expires': expires,
                              })
    except Exception as e:
        return -1, 'Error: connecting while connecting ({})'.format(e)

    if r.status_code != 200:
        return -1, 'Error: request went bad ({}) - {}'.format(r.status_code,
                                                              r.reason)

    return 0, r.text


# def _get_raw_dpaste_url(url):
#     """Return a valid URL for dpaste in raw mode (no HTML)"""
#     return url.strip('"') + '/raw'


def load_ipython_extension(ipython):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    pass


def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    pass


@register_line_cell_magic
def dpaste(line, cell=None, return_url=False):
    """Paste line or cell content to dpaste.de
    Or get code snippet from dpaste.de

    Usage, in line mode:
        %dpaste [-1[<x><h><d><w>]|-0] [-o] [-s] statement

    Usage, in cell mode:
        %%dpaste [-1[<x><h><d><w>]|-0]
          code...
          code...

    Options:
        -1x: expires after two views.
        -1h: expires after one hour (default).
        -1d: expires after one day.
        -1w: expires after one week.
        -0: never expires [NOT SUPPORTED BY DPASTE.DE].

        -o: return URL that can be stored in a variable (line mode only).
            Use $var to reuse URL in magic commands.
        -s: silent mode, without -o no way to get URL back (line mode only).

    Usage, in line mode:
        %dpaste -g [<dpaste hash>|<dpaste url>]

    Examples
    --------
    ::
      [1]: %dpaste print(42)
      https://dpaste.de/WXYZ

      [2]: %%dpaste -1m
         ...: print(42)
         ...:
      https://dpaste.de/WXYZ

      [3]: %dpaste -gWXYZ
         ...: print(42)
         ...:

      [4]: %dpaste -g https://dpaste.de/WXYZ
         ...: print(42)
         ...:

      [5]: url = %dpaste -o print(42)
         ...:
      https://dpaste.de/WXYZ

      [6]: url = %dpaste -o -s print(42)
         ...:

      [7]: %dpaste -g $url
         ...: print(42)
         ...:

    """
    try:
        options, stmt = getopt.getopt(line.split(), _DURATION_OPTIONS)
    except getopt.GetoptError as error:
        raise UsageError('Please check options')

    if cell is None:
        # May not reflect exact statement (if multiple whitespace)
        # Could be improve by removing found options from line...
        stmt = ' '.join(stmt)
    else:
        stmt = cell
        for c in range(-5, 0):
            print(ord(cell[c]))

    hash = [v for o, v in options if o == '-g']
    if len(hash) >= 1:
        # Take the first value
        url_mode = '-u' in {o for o, _ in options}
        _x = '-u ' + hash[0] if url_mode else hash[0]
        getdpaste(_x)
        return

    silent_mode = '-s' in {o for o, _ in options}
    output_url = '-o' in {o for o, _ in options}
    # Cell mode: myvar = %%dpaste -o something, unexpected behaviour happens
    # This would requires having two registered functions (one line, one cell)
    # for case detection, just to display a warning...

    # Compute duration if any (default 1h)
    expires = [(o, v) for o, v in options if o in {'-0', '-1'}]
    if expires == []:
        duration = _durations[DEFAULT_DURATION]
    elif len(expires) > 1:
        raise UsageError('Too many options for expiration')
    else:
        option = (expires[0][0] + expires[0][1])[-1] # Take last char -1X or -0
        if option in _durations.keys():
            duration = _durations[option]
        else:
            raise UsageError('Invalid expiration delay')

    status, msg = _post_to_dpaste(stmt, expires=duration)

    if status != 0:
        raise UsageError(msg)

    url = msg.strip('"')
    if not silent_mode:
        print(url)

    return url if return_url or output_url else None


class PreParser(HTMLParser):
    """HTML Parser for extracting raw text in <pre></pre> division as
    returned by dpaste.de
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = False
        self.pre = ""

    def handle_starttag(self, tag, attributes):
        if tag != 'pre':
            return
        self.recording = True

    def handle_endtag(self, tag):
        if tag == 'pre' and self.recording:
            self.recording = False

    def handle_data(self, data):
        if self.recording:
            self.pre += data


@register_line_magic
def getdpaste(line, cell=None):
    """Get code snippet from dpaste.de

    Usage, in line mode:
        %getdpaste [-u] [<dpaste hash>|<dpaste url>]

    Options:
        -u: prepends URL as Python comment.

    Examples
    --------
    ::
      [1]: %getdpaste WXYZ
         ...: print(42)
         ...:

      [2]: %getdpaste https://dpaste.de/WXYZ
         ...: print(42)
         ...:

      [3]: %getdpaste $url
         ...: print(42)
         ...:

    """
    try:
        options, stmt = getopt.getopt(line.split(), _GETDPASTE_OPTIONS)
    except getopt.GetoptError as error:
        raise UsageError('Please check options')

    url_mode = '-u' in {o for o, _ in options}

    if len(stmt) != 1:
        raise UsageError('Only one hash currently supported')
    else:
        stmt = stmt[0]

    if stmt.startswith(DPASTE_DE_URL):
        # Quit specific to dpaste.de
        url = stmt + ('' if stmt.endswith('/raw') else '/raw')
    else:
        url = GET_DPASTE_DE_URL.format(stmt)

    # dpaste.de has disabled raw mode as plain text due to abuse
    # It is now returning a HTML version.
    # Cannot yse %load magic to do the job anymore.
    ipython = get_ipython()
    contents = ipython.find_user_code(url) #TODO: catch HTTPError 404
    parser = PreParser()
    parser.feed(contents)
    ipython.set_next_input(f"#{url}\n\n" + parser.pre if url_mode else parser.pre,
                           replace=True)
    return
