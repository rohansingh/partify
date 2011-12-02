partify server
==============
Suggests playlists based on music preferences of users who
are geographically close to you.

Prequisites
-----------
* Python 3
* pip
* MongoDB

Setup
-----

    $ virtualenv . -p <your python3 path>
    $ . bin/activate
    (src)$ pip install -r requirements.txt
    (src)$ deactivate

Run
---
1.  Run MongoDB on the default port.

2.  In your shell:

        $ . bin/activate
        (src)$ python main.py
