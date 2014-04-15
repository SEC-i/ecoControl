import logging
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from server.models import RuleSet, Statement, Comparisons, OperandType, Task
from functions import get_statements_for_rule_set, save_rule_set
from helpers import create_json_response

logger = logging.getLogger('webapi')

def list_rule_sets(request, limit):
    output = []
    for rule_set in RuleSet.objects.filter(root = True):
        output.append(get_statements_for_rule_set(rule_set))
    return create_json_response(request, output)

def show_rule_set(request, rule_set_id):
    rule_set = get_statements_for_rule_set(RuleSet.objects.get(id = rule_set_id))
    return create_json_response(request, rule_set)

@require_POST
def set_rule_set(request, rule_set_id):
    return create_json_response(request, {"error": "Not yet implemented."})

@require_POST
def add_rule_set(request):
    if 'data' in request.POST:
        try:
            rule_set_data = json.loads(request.POST['data'])

            save_rule_set(rule_set_data, None)

            return create_json_response(request, {"status": "ok"})
        except KeyError:
            return create_json_response(request, {"status": "failed"})
    return create_json_response(request, {"status": "failed"})