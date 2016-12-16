from . import modules


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        aws_access_key = properties['aws_access_key']
        aws_access_secret_key = properties['aws_access_secret_key']
        aws_region = properties['aws_region']
        endpoint_url = self._filter_missing_endpoint(properties.get('aws_endpoint_url', ''))

        beans['aws_credentials'] = {
            'aws_access_key_id': aws_access_key,
            'aws_secret_access_key': aws_access_secret_key,
            'region_name': aws_region,
            'endpoint_url': endpoint_url
        }

    def after_setup(self, properties, arguments, context, beans_initializer):
        pass

    @staticmethod
    def _filter_missing_endpoint(endpoint_url):
        return endpoint_url if len(endpoint_url) > 0 else None


def get_credentials(context):
    return context.aws_credentials
