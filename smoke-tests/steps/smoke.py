from behave import *
import requests
import json

APPLICATION_URL = 'http://localhost:8080'


@given('GET argument {argument_name} equal to {argument_value}')
def step_impl(context, argument_name, argument_value):
    _setup_required_arguments(context)
    context.get_params[argument_name] = argument_value


@given('POST payload equal to {request_payload}')
def step_impl(context, request_payload):
    context.request_payload = json.loads(request_payload)


@when('GET is send to {context_path}')
def step_impl(context, context_path):
    _setup_required_arguments(context)
    context.response = requests.get('{}{}'.format(APPLICATION_URL, context_path), params=context.get_params)


@when('POST with payload is send to {context_path}')
def step_impl(context, context_path):
    context.response = requests.post('{}{}'.format(APPLICATION_URL, context_path), json=context.request_payload)


@then('Response status code should be equal to 200')
def step_impl(context):
    assert context.response.status_code == 200


@then('Valid response should be generated with data equal to {expected_data}')
def step_impl(context, expected_data):
    json_data = context.response.json()
    assert json_data['status'] == 'ok'
    assert json_data['data'] == expected_data


@then('Valid response should be generated with JSON response equal to {expected_json}')
def step_impl(context, expected_json):
    json_data = context.response.json()
    assert json_data['status'] == 'ok'
    assert json_data['data'] == json.loads(expected_json)


def _setup_required_arguments(context):
    if not hasattr(context, 'get_params'):
        context.get_params = {}
