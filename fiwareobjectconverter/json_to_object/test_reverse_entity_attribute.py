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

import sys
import unittest

from fiwareobjectconverter.json_to_object.reverse_entity_attribute import ReverseEntityAttribute


class TestEntityAttribute(unittest.TestCase):

    def test_reverse_entity_attribute_bool(self):
        dict_var = dict(type='boolean', value=True, metadata={})
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(True, rea.get_value())
        self.assertEqual(type(rea.get_value()), bool)

    def test_reverse_entity_attribute_int(self):
        dict_var = dict(type='number', value=1, metadata=dict(
            python=dict(type='dataType', value='int')))
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(1, rea.get_value())
        self.assertEqual(type(rea.get_value()), int)

    def test_reverse_entity_attribute_float(self):
        dict_var = dict(type='number', value=2.132, metadata=dict(
            python=dict(type='dataType', value='float')))
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(2.132, rea.get_value())
        self.assertEqual(type(rea.get_value()), float)

    def test_reverse_entity_attribute_long(self):
        if sys.version_info <= (3, 0):
            dict_var = dict(type='number', value=123456789123456789123, metadata=dict(
                python=dict(type='dataType', value='long')))
            rea = ReverseEntityAttribute(dict_var)
            # self.assertEqual(123456789123456789123, rea.get_value()) # Python2 is not able to convert it back properly
            self.assertEqual(type(rea.get_value()), long)

    def test_reverse_entity_attribute_complex(self):
        dict_var = dict(type='array',
                 value=[dict(type='number',   value=0,   metadata=dict(python=dict(type='dataType', value='int'))),
                        dict(type='number', value=2.34, metadata=dict(python=dict(type='dataType', value='int')))],
                 metadata=dict(python=dict(type='dataType', value='complex')))
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(2.34j, rea.get_value())
        self.assertEqual(type(rea.get_value()), complex)

    def test_reverse_entity_attribute_string(self):
        dict_var = dict(type='string', value='Hello world!', metadata={})
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual('Hello world!', rea.get_value())
        self.assertEqual(type(rea.get_value()), str)

    def test_reverse_entity_attribute_unicode(self):
        dict_var = dict(type='string', value=u'Unicode',
                 metadata=dict(python=dict(type='dataType', value='unicode')))
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(u'Unicode', rea.get_value())
        if sys.version_info <= (3, 0):
            self.assertEqual(type(rea.get_value()), unicode)
        else:
            self.assertEqual(type(rea.get_value()), str)

    def test_reverse_entity_attribute_tuple(self):
        dict_var = dict(type='array', value=[dict(type='number', value=1, metadata=dict(python=dict(type='dataType', value='int'))), dict(
            type='number', value=2, metadata=dict(python=dict(type='dataType', value='int')))], metadata=dict(python=dict(type='dataType', value='tuple')))
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(tuple((1, 2)), rea.get_value())
        self.assertEqual(type(rea.get_value()), tuple)

    def test_reverse_entity_attribute_list(self):
        dict_var = dict(
            type='array',
            value=[dict(type='number', value=1, metadata=dict(python=dict(type='dataType', value='int'))),
                   dict(type='number', value=2, metadata=dict(python=dict(type='dataType', value='int')))],
            metadata={})
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(list([1, 2]), rea.get_value())
        self.assertEqual(type(rea.get_value()), list)

    def test_reverse_entity_attribute_dict(self):
        dict_var = dict(type='object', value=dict(
            a=dict(type='number', value=1, metadata=dict(
                python=dict(type='dataType', value='int'))),
            b=dict(type='number', value=2, metadata=dict(python=dict(type='dataType', value='int')))),
            metadata={})

        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(dict(a=1, b=2), rea.get_value())
        self.assertEqual(type(rea.get_value()), dict)

    def test_reverse_entity_attribute_foreign_class(self):
        dict_var = dict(type='ClassInt',
                 value=dict(int=dict(type='number', value=1, metadata=dict(
                     python=dict(type='dataType', value='int')))),
                 metadata=dict(python='class'))

        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(dict(int=1), rea.get_value())
        self.assertEqual(type(rea.get_value()), dict)

    def test_reverse_entity_attribute_float_with_wrong_value(self):
        dict_var = dict(type='number', value='2.132', metadata=dict(
            python=dict(type='dataType', value='float')))
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(2.132, rea.get_value())
        self.assertEqual(type(rea.get_value()), float)

    def test_reverse_entity_attribute_int_with_wrong_value(self):
        dict_var = dict(type='number', value='1', metadata=dict(
            python=dict(type='dataType', value='int')))
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(1, rea.get_value())
        self.assertEqual(type(rea.get_value()), int)

    def test_reverse_entity_attribute_bool_with_wrong_value(self):
        dict_var = dict(type='boolean', value='False', metadata={})
        rea = ReverseEntityAttribute(dict_var)
        self.assertEqual(False, rea.get_value())
        self.assertEqual(type(rea.get_value()), bool)
