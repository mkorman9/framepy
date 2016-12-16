from . import modules


class Module(modules.Module):
    def before_setup(self, properties, arguments, beans):
        aws_access_key = properties['aws_access_key']
        aws_access_secret_key = properties['aws_access_secret_key']
        aws_region = properties['aws_region']

        beans['aws_credentials'] = {
            'aws_access_key_id': aws_access_key,
            'aws_secret_access_key': aws_access_secret_key,
            'region_name': aws_region
        }

    def after_setup(self, properties, arguments, context, beans_initializer):
        pass


def get_credentials(context):
    return context.aws_credentials
