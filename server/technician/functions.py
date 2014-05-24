import os
import logging
import json

logger = logging.getLogger('django')
SNIPPET_FOLDER = 'snippets/'


def get_snippet_list():
    output = []
    for filename in os.listdir(SNIPPET_FOLDER):
        if os.path.splitext(filename)[1] == ".py":
            output.append(filename)
    return output


def get_snippet_code(name):
    if name in get_snippet_list():
        with open(SNIPPET_FOLDER + name, "r") as snippet_file:
            return {'code': snippet_file.read()}
    return {'status': 'not found'}


def save_snippet(name, code):
    data = json.loads(request.body)
    if 'name' in data and 'code' in data:
        name = data['name']
        code = data['code']
        if os.path.splitext(name)[1] == ".py" and code != "":
            with open(SNIPPET_FOLDER + snippet, "w") as snippet_file:
                snippet_file.write(code)
            return {'status': 'success'}

    return {'status': 'failed'}
