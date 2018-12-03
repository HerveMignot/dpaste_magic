"""
Magic function that push or pull code snippets out of dpaste.

%dpaste answer = 42
returns a dpaste.de url for line.

%%dpaste
answer = 42
returns a dpaste url for cell.

%dpaste or %%dpaste {-1x -1h -1d -1w -0}
post with expires duration (-1x for one time/two views, -0 is forever).

%dpaste -g XYZ
answer = 42
retrieves snippet from XYZ url hash.

%getdpaste XYZ
answer = 42
retrieves snippet from XYZ url hash.

%dpaste -g <dpaste.de url>
answer = 42
retrieves snippet from dpaste.de url (with or without /raw).

%getdpaste -g <dpaste.de url>
answer = 42
retrieves snippet from dpaste.de url (with or without /raw).

"""

__version__ = '0.1.0'

import logging
import sys
import getopt
import requests

from contextlib import redirect_stdout
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
DURATION_OPTIONS = '1:g:os' # '01:g:os' with never

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
      https://dpaste.de/XYZ

      [2]: %%dpaste -1m
         ...: print(42)
         ...:
      https://dpaste.de/WYZ

      [3]: %dpaste -gWYZ
         ...: print(42)
         ...:

      [4]: %dpaste -g https://dpaste.de/WYZ
         ...: print(42)
         ...:

      [5]: url = %dpaste -o print(42)
         ...:
      https://dpaste.de/WYZ

      [6]: url = %dpaste -o -s print(42)
         ...:

      [7]: %dpaste -g $url
         ...: print(42)
         ...:

    """
    try:
        options, stmt = getopt.getopt(line.split(), DURATION_OPTIONS)
    except getopt.GetoptError as error:
        raise UsageError('Please check options')

    if cell is None:
        # May not reflect exact statement (if multiple whitespace)
        # Could be improve by removing found options from line...
        stmt = ' '.join(stmt)
    else:
        stmt = cell

    hash = [v for o, v in options if o == '-g']
    if len(hash) >= 1:
        # Take the first value
        getdpaste(hash[0])
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


@register_line_magic
def getdpaste(line, cell=None):
    """Get code snippet from dpaste.de

    Usage, in line mode:
        %getdpaste [<dpaste hash>|<dpaste url>]

    Examples
    --------
    ::
      [1]: %getdpaste WYZ
         ...: print(42)
         ...:

      [2]: %getdpaste https://dpaste.de/WYZ
         ...: print(42)
         ...:

      [3]: %getdpaste $url
         ...: print(42)
         ...:

    """
    if line.startswith(DPASTE_DE_URL):
        # Quit specific to dpaste.de
        url = line + ('' if line.endswith('/raw') else '/raw')
    else:
        url = GET_DPASTE_DE_URL.format(line)

    # Use %load magic to do the job.
    ipython = get_ipython()
    ipython.magic("load {}".format(url))
    return
