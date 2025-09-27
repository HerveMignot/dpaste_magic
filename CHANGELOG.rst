Changelog
=========

0.3.0 (2025-09-27):
-------------------

- Remove HTML parsing in getdpaste as /raw returns raw paste again.
- Add status_code management in getdpaste to raise exception when not 200.

0.2.1 (2019-12-14):
-------------------

- Change from dpaste.de to dpaste.org.
- Move to requests.get() to get dpaste because an User Agent is required.

0.2.0 (2019-11-24):
-------------------

- Add HTML parser to extract raw text in HTML `<pre>` div as now
  dpaste.org renders raw mode as HTML page, due to abuses.
  `%load` magic is not used anymore.
- Add -u option to getdpaste (also working with dpaste -u -g) to
  prepend dpaste.org URL at the top of pasted text.

0.1.2
-----

- Initial release.
