import sys
import turbocore
import os


PYTHON_WRAPPER = os.environ.get("PYTHON_WRAPPER", "python")

DEMO_ENDPOINTS = """import uuid
from typing import Optional
from flask import Flask, jsonify, request, make_response, url_for, redirect, render_template, abort, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy
from werkzeug.utils import secure_filename
import json
import os
import sys
import time
import datetime


from __main__ import authed


def setup_context(app, db):
    
    @app.route('/', methods=['GET', 'POST'])
    def X():
        authed()
        x = my_table()
        x.col_a = str(time.time())
        x.t = datetime.datetime.now(datetime.UTC)
        db.session.add(x)
        db.session.commit()
        return(jsonify({"hello":"world", "x": x.id, "t": x.t}))
        
    @app.route('/Y', methods=['GET', 'POST'])
    def Y():
        authed()
        if request.method == "POST":
            if 'thefile' not in request.files:
                return abort(401)
            else:
                file = request.files['thefile']
                if file.filename == "":
                    return abort(401)
                if file and True:
                    file.save("instance/TEST")

        return '<form method=post enctype=multipart/form-data><input style="height: 300px; width: 300px; background-color: darkorange;" type=file name=thefile onchange="form.submit();" /><input type=submit></form>'


    @app.route('/info', methods=['GET', 'POST'])
    def info():
        return(render_template("info.html"))

"""

PROGRAM_MAIN = """from typing import Optional
from flask import Flask, jsonify, request, make_response, url_for, redirect, render_template, abort, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy
from werkzeug.utils import secure_filename
import json
import os
import sys
import time
import datetime


def extract_bearer(req: request) -> str | None:
    auth = req.headers.get("Authorization", "")
    if not auth.upper().startswith("BEARER "):
        return None
    return auth[len("Bearer "):].strip()

    
def authed():
    auth = extract_bearer(request)
    if auth == None or auth != app.config["PSK_BEARER"]:
        abort(401)


if 'SQLALCHEMY_DATABASE_URI' not in os.environ.keys():
    print('SQLALCHEMY_DATABASE_URI not set as ENV')
    sys.exit(1)


class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI', "")
app.config["PSK_BEARER"] = os.environ.get('PSK_BEARER', "")
app.config['MAX_CONTENT_LENGTH'] = 500*1024*1024


db = SQLAlchemy(model_class=Base)

class my_table(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    col_a: Mapped[str] = mapped_column(sqlalchemy.String(80), unique=True)
    col_b: Mapped[Optional[int]] = mapped_column(sqlalchemy.Integer)
    s80: Mapped[Optional[str]] = mapped_column(sqlalchemy.String(80))
    t: Mapped[Optional[datetime.datetime]] = mapped_column(sqlalchemy.DateTime)


db.init_app(app)

with app.app_context() as ac:
    db.drop_all()
    db.create_all()

    



if __name__ == '__main__':
    import importlib
    impl_mod = importlib.import_module(os.environ.get("API_IMPL", ""))
    setup_context = getattr(impl_mod, "setup_context")
    setup_context(app, db)

    ssl_certfile = os.environ.get("SSLCERTFILE", "")
    ssl_keyfile = os.environ.get("SSLKEYFILE", "")
    if ssl_keyfile.strip() == "":
        print("*"*80)
        print("EXAMPLE")
        print('curl -L -H "Authorization: Bearer foo123" -X POST --data "a=b" http://127.0.0.1:8080/')
        print('curl -L -H "Authorization: Bearer foo123" -X POST -F "thefile=@server.py" http://127.0.0.1:8080/Y/')
        print("*"*80)
        app.run(host='0.0.0.0', port=8080, debug=True)
    else:
        print("*"*80)
        print("EXAMPLE")
        print('curl -L -H "Authorization: Bearer foo123" -X POST --data "a=b" https://127.0.0.1:4433/')
        print('curl -L -H "Authorization: Bearer foo123" -X POST -F "thefile=@server.py" http://127.0.0.1:8080/Y/')
        print("*"*80)
        app.run(host='0.0.0.0', port=4433, debug=True, ssl_context=(ssl_certfile, ssl_keyfile))
"""


def flama_simple(IDENTIFIER):
    os.makedirs(os.path.join(IDENTIFIER, "templates"), exist_ok=False)
    os.makedirs(os.path.join(IDENTIFIER, "endpoints"), exist_ok=False)
    
    endpointsfilename = os.path.join(IDENTIFIER, "endpoints", "__init__.py")
    with open(endpointsfilename, 'w') as f:
        f.write(DEMO_ENDPOINTS)
    mainfilename = os.path.join(IDENTIFIER, "server.py")
    with open(mainfilename, 'w') as f:
        f.write(PROGRAM_MAIN)
    startsslfilename = os.path.join(IDENTIFIER, "start_ssl.sh")
    with open(startsslfilename, 'w') as f:
        f.write("""#"/bin/bash


export SSLCERTFILE=
export SSLKEYFILE=
export SQLALCHEMY_DATABASE_URI="sqlite:///nil.sql3"
export PSK_BEARER=foo123
export API_IMPL=endpoints
%s server.py
""" % (PYTHON_WRAPPER))
    os.chmod(startsslfilename, 0o700)

    startnosslfilename = os.path.join(IDENTIFIER, "start_nossl.sh")
    with open(startnosslfilename, 'w') as f:
        f.write("""#"/bin/bash


export SQLALCHEMY_DATABASE_URI="sqlite:///nil.sql3"
export PSK_BEARER=foo123
export API_IMPL=endpoints
%s server.py
""" % (PYTHON_WRAPPER))
    os.chmod(startnosslfilename, 0o700)


def main():
    turbocore.cli_this(__name__, 'flama_')
