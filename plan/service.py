from bottle import response
from json import dumps
from bottle import route, run, request, template
from plan import plan
import json
import os
from bottle import jinja2_view, route, static_file


here = os.path.dirname(__file__)
templates = os.path.join(here, 'templates')
static = os.path.join(here, 'static')


@route('/api/plan')
def api_plan():
    vma = request.params.get("vma", 15)
    res = {'plan': plan(vma=float(vma)).json()}
    response.content_type = "application/json"
    return json.dumps(res)


@route('/plan')
@jinja2_view('plan.html', template_lookup=[templates])
def _plan():
    return {'plan': plan().json()}

@route('/')
@jinja2_view('index.html', template_lookup=[templates])
def index():
    return {}


@route('/vma')
@jinja2_view('vma.html', template_lookup=[templates])
def vma():
    return {}


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=static)

run(host='localhost', port=8080)


