# dpaste_magic
Magic function that pushes or pulls code snippets out of pastebins.
dpaste.de is currently supported.

### Pushing code & cells
<pre>
  %dpaste answer = 42
  <i>https://dpaste.de/XYZ</i>
</pre>
pushes line content & print the dpaste url.
<pre>
  %%dpaste
  answer = 42
  <i>https://dpaste.de/XYZ</i>
</pre>
pushes cell content & print the dpaste url.
<pre>
  %%dpaste {-1x -1h -1d -1w -0}
  answer = 42
  <i>https://dpaste.de/XYZ</i>
</pre>
returns a dpaste url with expires duration:
* -1x: just for one read
* -1h: one hour (default)
* -1d: one day
* -1w: one week
* -0: never
These are the supported expiration time supported by dpaste.de.

Options:
* -o: return URL as value (for storage in a variable)
* -s: silent mode (URL not printed)

`my_url = %dpaste -o answer = 42`
push code on line, prints & stores url in `my_url` variable.

`my_url = %dpaste -o -s answer = 42`
push code on line & stores url in `my_url` variable (silent mode, no print).

### Getting back the paste
<pre>
  %getdpaste XYZ
</pre>
retrieves snippet from XYZ dpaste hash or URL and changes cell to:
<pre>
  # %load https://dpaste.de/XYZ/raw
  answer = 42
</pre>

With `%dpaste -g` get option:
<pre>
  %dpaste -g XYZ
</pre>
retrieves snippet from XYZ dpaste hash or URL and changes cell to:
<pre>
  # %load https://dpaste.de/XYZ/raw
  answer = 42
</pre>


## Installation

Use:
`pip install dpaste_magic`
to install the magic command.

First load the magic in a cell:

`%load_ext dpaste_magic`

and then use the function in your cell to dpaste its content.

`%%dpaste`, `%dpaste` or `%getdpaste`.


## TO DO

* increase tests range
* code unload function
