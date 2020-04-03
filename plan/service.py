from bottle import response
from json import dumps
from bottle import route, run, request, template
from plan.generator import plan, SessionType
import json
import os
from bottle import jinja2_view, route, static_file
import bottle


here = os.path.dirname(__file__)
templates = os.path.join(here, "templates")
static = os.path.join(here, "static")


@route("/api/plan")
def api_plan():
    vma = request.params.get("vma", 15)
    weeks = int(request.params.get("weeks", 8))
    race = SessionType(int(request.params.get("race", SessionType.TEN)))
    spw = int(request.params.get("spw", 5))

    res = {"plan": plan(vma=float(vma), race=race, weeks=weeks, spw=spw).json()}
    response.content_type = "application/json"
    return json.dumps(res)


@route("/plan")
@jinja2_view("plan.html", template_lookup=[templates])
def _plan():
    return {"plan": plan().json()}


@route("/guide")
@jinja2_view("guide.html", template_lookup=[templates])
def guide():
    return {}


@route("/")
@jinja2_view("index.html", template_lookup=[templates])
def index():
    return {}


@route("/vma")
@jinja2_view("vma.html", template_lookup=[templates])
def vma():
    return {}


@route("/static/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root=static)


if __name__ == '__main__':
    run(host="localhost", port=8787)
else:
    app = application = bottle.default_app()
