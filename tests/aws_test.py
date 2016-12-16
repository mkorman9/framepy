from assertpy import assert_that

from framepy import aws
import unittest


class AwsModuleTest(unittest.TestCase):
    def setUp(self):
        self.module = aws.Module()

    def test_should_setup_credentials_from_properties(self):
        # given
        key = 'key'
        secret_key = 'secret'
        region = 'us-west'
        properties = {
            'aws_access_key': key,
            'aws_access_secret_key': secret_key,
            'aws_region': region
        }

        beans = {}

        # when
        self.module.before_setup(properties, None, beans)

        # then
        assert_that(beans['aws_credentials']).is_equal_to(
            {
                'aws_access_key_id': key,
                'aws_secret_access_key': secret_key,
                'region_name': region
            }
        )
