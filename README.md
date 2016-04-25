utvsapi-ripozo
==============

A REST-like read-only API for [ÚTVS ČVUT](https://rozvoj.fit.cvut.cz/Main/rozvrhy-utvs-db)
implemented in [ripozo](http://ripozo.readthedocs.org/en/latest/).

To use this, create file named `mysql.cnf` with your MySQL credentials, see an example here:

    [client]
    host = localhost
    user = username
    database = dbname
    password = insecurepassword

This has been developed and run on Python 3 only, legacy Python might not work.

Install `flask-ripozo`, `ripozo-sqlalchemy`, `Flask-SQLAlchemy` and `mysqlclient` (you'll need mysql devel package for that). You might do it with virtualenv:

    pyvenv venv
    . venv/bin/activate
    pip install flask-ripozo ripozo-sqlalchemy Flask-SQLAlchemy mysqlclient

Start the service in debug mode:

    PYTHONPATH=. python3 utvsapi/main.py

Or run with gunicorn:

    pip install gunicorn
    PYTHONPATH=. gunicorn utvsapi.main:app

License
-------

Copyright (C) 2016  Miro Hrončok <miro@hroncok.cz>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

See LICENSE file for full license text.
