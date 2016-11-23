import unittest
import framepy.web
from assertpy import assert_that


class FormBindingTest(unittest.TestCase):
    def test_empty_form_should_be_mapped(self):
        # given
        class EmptyForm(object):
            pass

        form_data = {}

        # when
        binder = framepy.web.FormBinder(form_data, EmptyForm)

        # then
        assert_that(binder.has_errors()).is_false()
        assert_that(binder.entity).is_not_none()

    def test_should_fail_if_missing_required_param(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True)

        form_data = {}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_true()
        assert_that('name').is_equal_to(binder.errors[0]['field'])
        assert_that('MISSING_FIELD').is_equal_to(binder.errors[0]['error'])

    def test_should_not_fail_if_passed_required_param(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True)

        form_data = {'name':'xyz'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_false()
        assert_that(binder.entity).is_not_none()
        assert_that(binder.entity.name).is_equal_to('xyz')

    def test_should_not_fail_if_passed_optional_param(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=False)

        form_data = {'name':'xyz'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_false()
        assert_that(binder.entity).is_not_none()
        assert_that(binder.entity.name).is_equal_to('xyz')

    def test_should_not_fail_if_missing_optional_param(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=False)

        form_data = {}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_false()
        assert_that(binder.entity).is_not_none()

    def test_should_fail_if_wrong_type(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True, type='int')

        form_data = {'name': 'asdf'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_true()
        assert_that(binder.errors[0]['field']).is_equal_to('name')
        assert_that(binder.errors[0]['error']).is_equal_to('BAD_TYPE')

    def test_should_fail_if_string_too_long(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True, max=10, type='string')

        form_data = {'name': '12345678901'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_true()
        assert_that(binder.errors[0]['field']).is_equal_to('name')
        assert_that(binder.errors[0]['error']).is_equal_to('MAX_LENGTH')

    def test_should_fail_if_int_too_big(self):
        # given
        class SingleParamForm(object):
            age = framepy.web.FormConstraint('age', required=True, max=10, type='int')

        form_data = {'age': 11}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_true()
        assert_that(binder.errors[0]['field']).is_equal_to('age')
        assert_that(binder.errors[0]['error']).is_equal_to('MAX')

    def test_should_fail_if_string_too_short(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True, min=10, type='string')

        form_data = {'name': '123456789'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_true()
        assert_that(binder.errors[0]['field']).is_equal_to('name')
        assert_that(binder.errors[0]['error']).is_equal_to('MIN_LENGTH')

    def test_should_fail_if_int_too_small(self):
        # given
        class SingleParamForm(object):
            age = framepy.web.FormConstraint('age', required=True, min=10, type='int')

        form_data = {'age': 9}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        assert_that(binder.has_errors()).is_true()
        assert_that(binder.errors[0]['field']).is_equal_to('age')
        assert_that(binder.errors[0]['error']).is_equal_to('MIN')

    def test_should_validate_nested_form(self):
        # given
        class MultipleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True, min=4, max=10, type='string')
            age = framepy.web.FormConstraint('age', required=True, min=18, max=100, type='int')

        class OutterForm(object):
            inner = framepy.web.FormConstraint('inner', required=True, nested=MultipleParamForm)

        form_data = {'inner': {'name':'Michael', 'age':20}}

        # when
        binder = framepy.web.FormBinder(form_data, OutterForm)

        # then
        assert_that(binder.has_errors()).is_false()
        assert_that(binder.entity).is_not_none()
        assert_that(binder.entity.inner.name).is_equal_to('Michael')
        assert_that(binder.entity.inner.age).is_equal_to(20)

    def test_should_fail_in_nested_form(self):
        # given
        class MultipleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True, min=4, max=10, type='string')
            age = framepy.web.FormConstraint('age', required=True, min=18, max=100, type='int')

        class OutterForm(object):
            inner = framepy.web.FormConstraint('inner', required=True, nested=MultipleParamForm)

        form_data = {'inner': {'name':'Jon', 'age':15}}

        # when
        binder = framepy.web.FormBinder(form_data, OutterForm)

        # then
        assert_that(binder.has_errors()).is_true()
        assert_that(len(binder.errors)).is_equal_to(2)
        assert_that(binder.errors[0]['field'] == 'name' or binder.errors[1]['field'] == 'name').is_true()
        assert_that(binder.errors[0]['field'] == 'name' or binder.errors[1]['field'] == 'age').is_true()
        assert_that(binder.errors[0]['error'] == 'MIN_LENGTH' or binder.errors[1]['error'] == 'MIN_LENGTH').is_true()
        assert_that(binder.errors[0]['error'] == 'MIN' or binder.errors[1]['error'] == 'MIN').is_true()
