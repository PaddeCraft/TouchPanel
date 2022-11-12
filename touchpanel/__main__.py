# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

# Server Stuff
from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

# Misc
import socket as _socket
import urllib.parse
import threading
import pathlib
import logging
import random
import string
import shutil
import base64
import json
import time
import os

# Cuid
from cuid import cuid

# ---------------------------------------------------------------------------- #
#                             Initialize variables                             #
# ---------------------------------------------------------------------------- #
cfgPath = os.path.join(os.path.expanduser("~"), ".PaddeCraftSoftware", "TouchPanel")
app = Flask("TouchPanel", root_path=pathlib.Path(__file__).parent.absolute())
app.config["SECRET_KEY"] = "SECRET-" + (
    "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(128))
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(cfgPath, "data.db")
pathlib.Path(cfgPath).mkdir(exist_ok=True, parents=True)
db = SQLAlchemy(app)
socket = SocketIO(app)
closeTab = "<script>window.close()</script>"
pageSizes = [
    {"id": 1, "name": "5x3"},
    {"id": 2, "name": "7x5"},
    {"id": 3, "name": "9x6"},
    {"id": 4, "name": "15x10"},
]

# ---------------------------------------------------------------------------- #
#                             Prevent flask logger                             #
# ---------------------------------------------------------------------------- #


logging.getLogger("werkzeug").disabled = True


# ---------------------------------------------------------------------------- #
#                                Database models                               #
# ---------------------------------------------------------------------------- #
class Page(db.Model):
    cuid = db.Column(db.String(32), primary_key=True, unique=True)
    name = db.Column(db.String(32))
    main = db.Column(db.Boolean)
    type = db.Column(db.Integer)
    # Types cols x rows
    # 1: 5x3
    # 2: 7x5
    # 3: 9x6
    # 4: 15x10


class Button(db.Model):
    cuid = db.Column(db.String(32), primary_key=True, unique=True)
    pageCuid = db.Column(db.String(32))
    index = db.Column(db.Integer)
    name = db.Column(db.String(32))
    icon = db.Column(db.String(128))
    action = db.Column(db.String(128))


# ---------------------------------------------------------------------------- #
#                       Create everything if not existing                      #
# ---------------------------------------------------------------------------- #
if not os.path.isfile(os.path.join(cfgPath, "data.db")):
    print("Generating example page...")
    os.makedirs(os.path.join(cfgPath, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(cfgPath, "icons"), exist_ok=True)
    with open(os.path.join(cfgPath, "scripts", "noneaction.py"), "w+") as f:
        f.write("exit(0)")
    with app.app_context():
        db.create_all()
        examplePage = Page(cuid=cuid(), name="Example Page", main=True, type=1)
        db.session.add(examplePage)
        for x in range(12):
            exampleBtn = Button(
                cuid=cuid(),
                index=x,
                pageCuid=examplePage.cuid,
                name="Nothingness " + str(x + 1),
                icon="cross.jpg",
                action="noneaction.py",
            )
            db.session.add(exampleBtn)
        db.session.commit()
    shutil.copyfile(
        os.path.join(pathlib.Path(__file__).parent.absolute(), "cross.jpg"),
        os.path.join(cfgPath, "icons", "cross.jpg"),
    )

# ---------------------------------------------------------------------------- #
#                                Code functions                                #
# ---------------------------------------------------------------------------- #
def _loadPage(id):
    emit("loadpage", generatePageJson(id))


# ---------------------------------------------------------------------------- #
#                               Helper functions                               #
# ---------------------------------------------------------------------------- #
def execPyCode(code, btnid):
    exec(code, {"btnid": btnid, "loadPage": _loadPage})


def generatePageJson(pageCuid):
    page = Page.query.filter_by(cuid=pageCuid).first()
    data = {
        "cuid": page.cuid,
        "name": page.name,
        "type": page.type,
        "buttons": [],
        "pages": [],
    }
    for pge in Page.query.all():
        data["pages"].append({"name": pge.name, "cuid": pge.cuid})
    for btn in Button.query.filter_by(pageCuid=page.cuid).all():
        data["buttons"].append(
            {"cuid": btn.cuid, "name": btn.name, "icon": btn.icon, "index": btn.index}
        )
    return data


# ---------------------------------------------------------------------------- #
#                              Socket interactions                             #
# ---------------------------------------------------------------------------- #
@socket.on("run")
def runaction(btnid):
    btn = Button.query.filter_by(cuid=btnid).first()
    file = btn.action
    try:
        with open(os.path.join(cfgPath, "scripts", file), encoding="UTF-8") as f:
            content = f.read()
        execPyCode(content, btnid)
    except Exception as e:
        emit("actionError", {"msg": str(e), "fname": file})


@socket.on("loadLandingPage")
def loadLandingPage():
    emit("loadpage", generatePageJson(Page.query.filter_by(main=True).first().cuid))


@socket.on("loadPage")
def loadPage(id):
    emit("loadpage", generatePageJson(id))


# ---------------------------------------------------------------------------- #
#                               HTTP interactions                              #
# ---------------------------------------------------------------------------- #
@app.route("/icon/<file>/")
def loadIcon(file):
    return send_file(os.path.join(cfgPath, "icons", file))


@app.route("/")
def main():
    return render_template("main.html", edit=False)


@app.route("/edit")
def edit():
    return render_template("main.html", edit=True)


@app.route("/edit/btn", methods=["GET", "POST"])
def editBtn():
    if request.method == "GET":
        actions = os.listdir(os.path.join(cfgPath, "scripts"))
        icons = os.listdir(os.path.join(cfgPath, "icons"))
        if request.args.get("mode") == "new":
            return render_template(
                "editbtn.html",
                actions=actions,
                icons=icons,
                action=actions[0],
                isNew=False,
                icon=icons[0],
            )
        else:
            btn = Button.query.filter_by(cuid=request.args.get("id")).first()
            action = btn.action
            name = btn.name
            icon = btn.icon

            btnData = {"name": btn.name, "icon": btn.icon, "action": btn.action}

            with open(os.path.join(cfgPath, "icons", btn.icon), "rb") as _icon:
                btnData["icon_b64"] = base64.b64encode(_icon.read()).decode("utf-8")

            with open(os.path.join(cfgPath, "scripts", btn.action), "rb") as _action:
                btnData["script_64"] = base64.b64encode(_action.read()).decode("utf-8")

            return render_template(
                "editbtn.html",
                btnData=urllib.parse.quote(json.dumps(btnData)),
                actions=actions,
                icons=icons,
                action=action,
                isNew=False,
                name=name,
                icon=icon,
            )
    else:
        new = request.args.get("mode") == "new"
        page = request.args.get("page")
        name = request.form.get("name")
        icon = request.form.get("icon")
        action = request.form.get("action")
        if new:
            index = request.args.get("idx")
            btn = Button(
                cuid=cuid(),
                pageCuid=page,
                name=name,
                icon=icon,
                action=action,
                index=index,
            )
            db.session.add(btn)
            db.session.commit()
        else:
            id = request.args.get("id")
            btn = Button.query.filter_by(cuid=id).first()
            btn.name = name
            btn.icon = icon
            btn.action = action
            db.session.commit()
        emit("loadpage", generatePageJson(page), namespace="/", broadcast=True)
    return closeTab


@app.route("/edit/deletebtn")
def deleteBtn():
    id = request.args.get("id")
    page = request.args.get("page")
    btn = Button.query.filter_by(cuid=id).first()
    db.session.delete(btn)
    db.session.commit()
    emit("loadpage", generatePageJson(page), namespace="/", broadcast=True)
    return closeTab


@app.route("/edit/deletepage")
def deletePage():
    id = request.args.get("id")
    page = Page.query.filter_by(cuid=id).first()
    if page.main:
        Page.query.filter_by(main=False).first().main = True
    db.session.delete(page)
    loadid = Page.query.filter_by(main=True).first().cuid
    emit("loadpage", generatePageJson(loadid), namespace="/", broadcast=True)
    db.session.commit()
    return closeTab


@app.route("/edit/makemain")
def makePageMain():
    id = request.args.get("page")
    old = Page.query.filter_by(main=True).first()
    old.main = False
    new = Page.query.filter_by(cuid=id).first()
    new.main = True
    db.session.commit()
    return "Success"


@app.route("/edit/page", methods=["GET", "POST"])
def editPage():
    edit = request.args.get("mode") == "edit"
    if request.method == "GET":
        pagecount = Page.query.count()
        if edit:
            page = Page.query.filter_by(cuid=request.args.get("page")).first()
            return render_template(
                "editpage.html",
                edit=True,
                pagecnt=pagecount,
                sizes=pageSizes,
                name=page.name,
            )
        else:
            return render_template(
                "editpage.html",
                edit=False,
                pagecnt=pagecount,
                sizes=pageSizes,
                name="",
            )
    else:
        if edit:
            page = Page.query.filter_by(cuid=request.args.get("page")).first()
            page.name = request.form.get("name")
            db.session.commit()
            emit("loadpage", generatePageJson(page.cuid), namespace="/", broadcast=True)
        else:
            page = Page(
                cuid=cuid(),
                name=request.form.get("name"),
                main=False,
                type=request.form.get("type"),
            )
            db.session.add(page)
            db.session.commit()
            emit("loadpage", generatePageJson(page.cuid), namespace="/", broadcast=True)
        return closeTab


# ---------------------------------------------------------------------------- #
#                                 Run function                                 #
# ---------------------------------------------------------------------------- #
def run():
    def notifyUp():
        time.sleep(1.4)
        print("\nThe server should be up.")
        print("Detecting ip address...")
        # Get ip, source: https://stackoverflow.com/a/1267524
        ip = (
            (
                [
                    ip
                    for ip in _socket.gethostbyname_ex(_socket.gethostname())[2]
                    if not ip.startswith("127.")
                ]
                or [
                    [
                        (s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close())
                        for s in [_socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)]
                    ][0][1]
                ]
            )
            + [None]
        )[0]
        if ip == None:
            print("Couldn't detect your ip address.")
        else:
            print("Running on " + ip + ":8811")
        print("\nPress ^C to stop the server.")

    print("Starting Server...")
    threading.Thread(target=notifyUp).start()
    socket.run(app, host="0.0.0.0", port="8811", allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    print("It`s recommended run TouchPanel using the 'touchpanel' command.")
    run()
