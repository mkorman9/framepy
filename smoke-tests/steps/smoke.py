from behave import *
import requests

APPLICATION_URL = 'http://localhost:8080'


@given('GET argument {argument_name} equal to {argument_value}')
def step_impl(context, argument_name, argument_value):
    _setup_required_arguments(context)
    context.get_params[argument_name] = argument_value


@when('GET is send to {context_path}')
def step_impl(context, context_path):
    _setup_required_arguments(context)
    context.response = requests.get('{}{}'.format(APPLICATION_URL, context_path), params=context.get_params)


@then('Valid response should be generated with data equals to {expected_data}')
def step_impl(context, expected_data):
    assert context.response.status_code == 200

    json_data = context.response.json()
    assert json_data['status'] == 'ok'
    assert json_data['data'] == expected_data


def _setup_required_arguments(context):
    if not hasattr(context, 'get_params'):
        context.get_params = {}
