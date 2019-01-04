# dpaste_magic
Magic function that pushes or pulls code snippets out of pastebins.
dpaste.de is currently supported.

    %dpaste answer = 42
    https://dpaste.de/aBCD

pushes line content & print the dpaste url.

    %%dpaste
    answer = 42
    https://dpaste.de/aBCD

pushes cell content & print the dpaste url.

    %%dpaste {-1x -1h -1d -1w -0}
    answer = 42
    https://dpaste.de/aBCD

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

  %dpaste -g XYZ
  answer = 42

retrieves snippet from XYZ dpaste hash or URL.

  %getdpaste XYZ
  answer = 42
  
retrieves snippet from XYZ dpaste hash or URL (alias for `dpaste -g`).


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
