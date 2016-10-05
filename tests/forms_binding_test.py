import unittest
import framepy.web


class FormBindingTest(unittest.TestCase):
    def test_empty_form_should_be_mapped(self):
        # given
        class EmptyForm(object):
            pass

        form_data = {}

        # when
        binder = framepy.web.FormBinder(form_data, EmptyForm)

        # then
        self.assertFalse(binder.has_errors())
        self.assertIsNotNone(binder.form)

    def test_should_fail_if_missing_required_param(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True)

        form_data = {}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertTrue(binder.has_errors())
        self.assertEquals('name', binder.errors[0]['field'])
        self.assertEquals('MISSING_FIELD', binder.errors[0]['error'])

    def test_should_not_fail_if_passed_required_param(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True)

        form_data = {'name':'xyz'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertFalse(binder.has_errors())
        self.assertIsNotNone(binder.form)
        self.assertEqual('xyz', binder.form.name)

    def test_should_not_fail_if_passed_optional_param(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=False)

        form_data = {'name':'xyz'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertFalse(binder.has_errors())
        self.assertIsNotNone(binder.form)
        self.assertEqual('xyz', binder.form.name)

    def test_should_not_fail_if_missing_optional_param(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=False)

        form_data = {}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertFalse(binder.has_errors())
        self.assertIsNotNone(binder.form)

    def test_should_fail_if_wrong_type(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True, type='int')

        form_data = {'name': 'asdf'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertTrue(binder.has_errors())
        self.assertEqual('name', binder.errors[0]['field'])
        self.assertEqual('BAD_TYPE', binder.errors[0]['error'])

    def test_should_fail_if_string_too_long(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True, max=10, type='string')

        form_data = {'name': '12345678901'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertTrue(binder.has_errors())
        self.assertEqual('name', binder.errors[0]['field'])
        self.assertEqual('MAX_LENGTH', binder.errors[0]['error'])

    def test_should_fail_if_int_too_big(self):
        # given
        class SingleParamForm(object):
            age = framepy.web.FormConstraint('age', required=True, max=10, type='int')

        form_data = {'age': 11}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertTrue(binder.has_errors())
        self.assertEqual('age', binder.errors[0]['field'])
        self.assertEqual('MAX', binder.errors[0]['error'])

    def test_should_fail_if_string_too_short(self):
        # given
        class SingleParamForm(object):
            name = framepy.web.FormConstraint('name', required=True, min=10, type='string')

        form_data = {'name': '123456789'}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertTrue(binder.has_errors())
        self.assertEqual('name', binder.errors[0]['field'])
        self.assertEqual('MIN_LENGTH', binder.errors[0]['error'])

    def test_should_fail_if_int_too_small(self):
        # given
        class SingleParamForm(object):
            age = framepy.web.FormConstraint('age', required=True, min=10, type='int')

        form_data = {'age': 9}

        # when
        binder = framepy.web.FormBinder(form_data, SingleParamForm)

        # then
        self.assertTrue(binder.has_errors())
        self.assertEqual('age', binder.errors[0]['field'])
        self.assertEqual('MIN', binder.errors[0]['error'])

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
        self.assertFalse(binder.has_errors())
        self.assertIsNotNone(binder.form)
        self.assertEqual('Michael', binder.form.inner.name)
        self.assertEqual(20, binder.form.inner.age)

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
        self.assertTrue(binder.has_errors())
        self.assertEqual(2, len(binder.errors))
        self.assertTrue(binder.errors[0]['field'] == 'name' or binder.errors[1]['field'] == 'name')
        self.assertTrue(binder.errors[0]['field'] == 'name' or binder.errors[1]['field'] == 'age')
        self.assertTrue(binder.errors[0]['error'] == 'MIN_LENGTH' or binder.errors[1]['error'] == 'MIN_LENGTH')
        self.assertTrue(binder.errors[0]['error'] == 'MIN' or binder.errors[1]['error'] == 'MIN')
