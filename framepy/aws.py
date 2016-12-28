from . import modules
from . import _utils


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        aws_access_key = _utils.resolve_property_or_report_error(
            properties=properties,
            key='aws_access_key',
            log_message='[AWS] No aws_access_key found in properties'
        )
        aws_access_secret_key = _utils.resolve_property_or_report_error(
            properties=properties,
            key='aws_access_secret_key',
            log_message='[AWS] No aws_access_secret_key found in properties'
        )
        aws_region = _utils.resolve_property_or_report_error(
            properties=properties,
            key='aws_region',
            log_message='[AWS] No aws_region found in properties'
        )
        endpoint_url = _utils.resolve_property_or_report_error(
            properties=properties,
            key='aws_endpoint_url',
            log_message='[AWS] No aws_endpoint_url found in properties'
        )

        beans['aws_credentials'] = {
            'aws_access_key_id': aws_access_key,
            'aws_secret_access_key': aws_access_secret_key,
            'region_name': aws_region,
            'endpoint_url': endpoint_url
        }

    def after_setup(self, properties, arguments, context, beans_initializer):
        pass


def get_credentials(context):
    return context.aws_credentials
