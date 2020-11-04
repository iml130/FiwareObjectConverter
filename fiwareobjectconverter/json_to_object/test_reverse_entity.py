#    Copyright 2018 Fraunhofer IML
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import unittest

from fiwareobjectconverter.json_to_object.reverse_entity import ReverseEntity


class TestReverseEntity(unittest.TestCase):

    def test_reverse_entity_initialize_is_not_empty(self):
        dict_var = dict(type='MyJSONType', id='MyJSONTypeID', variableName=dict(type='number',
                    value=1, metadata=dict(python=dict(type='dataType', value='int'))))

        reverse_entity = ReverseEntity(**dict_var)
        self.assertEqual(getattr(reverse_entity, 'type'), 'MyJSONType')
        self.assertEqual(getattr(reverse_entity, 'id'), 'MyJSONTypeID')
        self.assertEqual(reverse_entity.payload, dict(variableName=dict(
            type='number', value=1, metadata=dict(python=dict(type='dataType', value='int')))))

    def test_reverse_entity_initialize_is_empty_payload(self):
        dict_var = dict(type='MyJSONType', id='MyJSONTypeID')

        reverse_entity = ReverseEntity(**dict_var)
        self.assertEqual(getattr(reverse_entity, 'type'), 'MyJSONType')
        self.assertEqual(getattr(reverse_entity, 'id'), 'MyJSONTypeID')
        self.assertEqual(reverse_entity.payload, {})

    def test_reverse_entitiyset_obejct_instantiate(self):
        dict_var = dict(type='MyJSONType', id='MyJSONTypeID', variableName=dict(type='number',
                    value=1, metadata=dict(python=dict(type='dataType', value='int'))))
        reverse_entity = ReverseEntity(**dict_var)
        self.assertEqual(getattr(reverse_entity, 'type'), 'MyJSONType')
        self.assertEqual(getattr(reverse_entity, 'id'), 'MyJSONTypeID')
        self.assertEqual(reverse_entity.payload,
                         dict(variableName=dict(type='number', value=1,
                            metadata=dict(python=dict(type='dataType', value='int')))))

        test_json = TestJson()
        reverse_entity.set_object(test_json)

        self.assertEqual(test_json.variable_name, 1)
        self.assertEqual(test_json.not_defined_var_by_json, 42)

    def test_reverse_entitiyset_obejct_instantiate_ignore_wrong_data_types(self):
        dict_var = dict(type='MyJSONType', id='MyJSONTypeID', variableName=dict(
            type='number', value=1.5, metadata=dict(python=dict(type='dataType', value='float'))))
        reverse_entity = ReverseEntity(**dict_var)
        self.assertEqual(getattr(reverse_entity, 'type'), 'MyJSONType')
        self.assertEqual(getattr(reverse_entity, 'id'), 'MyJSONTypeID')
        self.assertEqual(reverse_entity.payload,
                         dict(variableName=dict(type='number', value=1.5,
                                metadata=dict(python=dict(type='dataType', value='float')))))

        test_json = TestJson()
        reverse_entity.set_object(test_json, ignore_wrong_data_type=True)

        self.assertEqual(test_json.variable_name, 1.5)
        self.assertEqual(type(test_json.variable_name), float)
        self.assertEqual(test_json.not_defined_var_by_json, 42)

    def test_reverse_entitiyset_object_instantiate_set_attr_true(self):
        dict_var = dict(type='MyJSONType', id='MyJSONTypeID', variableName=dict(
                    type='number', value=1.5, metadata=dict(python=dict(type='dataType', value='float'))))
        reverse_entity = ReverseEntity(**dict_var)
        self.assertEqual(getattr(reverse_entity, 'type'), 'MyJSONType')
        self.assertEqual(getattr(reverse_entity, 'id'), 'MyJSONTypeID')
        self.assertEqual(reverse_entity.payload, dict(variableName=dict(
            type='number', value=1.5, metadata=dict(python=dict(type='dataType', value='float')))))

        test_json = TestJson()
        reverse_entity.set_object(test_json, set_attr=True)

        self.assertEqual(test_json.variable_name, 1.5)
        self.assertEqual(type(test_json.variable_name), float)
        self.assertEqual(test_json.not_defined_var_by_json, 42)

    def test_reverse_entitiyset_object_instantiate_set_attr_false(self):
        dict_var = dict(type='MyJSONType', id='MyJSONTypeID', variableName=dict(
            type='number', value=1.5, metadata=dict(python=dict(type='dataType', value='float'))))
        reverse_entity = ReverseEntity(**dict_var)
        self.assertEqual(getattr(reverse_entity, 'type'), 'MyJSONType')
        self.assertEqual(getattr(reverse_entity, 'id'), 'MyJSONTypeID')
        self.assertEqual(reverse_entity.payload, dict(variableName=dict(
            type='number', value=1.5, metadata=dict(python=dict(type='dataType', value='float')))))

        test_json = TestJson()
        try:
            reverse_entity.set_object(test_json, set_attr=False)
            self.fail()
        except TypeError:
            pass
            # Success!!


class TestJson(object):
    def __init__(self):
        self.variable_name = 0  # Set type int!
        self.not_defined_var_by_json = 42
