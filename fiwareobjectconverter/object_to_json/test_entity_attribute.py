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
import json
import sys

from fiwareobjectconverter.object_to_json.entity_attribute import EntityAttribute
from fiwareobjectconverter.object_to_json.entity import Entity


class TestEntityAttribute(unittest.TestCase):

    def test_entity_attribute_completely(self):
        # General functionality given.
        entity = Entity()
        entity.set_object(ComplexExample(), {}, False)
        ComplexExample().to_json(entity)
        # No Error thrown

    def test_entity_attribute_bool(self):
        entity_attribute = EntityAttribute(True, False)
        self.assertTrue(not hasattr(entity_attribute, 'metadata'))
        self.assertEqual(entity_attribute.value, True)
        self.assertEqual(entity_attribute.type, 'boolean')

        entity_attribute = EntityAttribute(False, False)
        self.assertTrue(not hasattr(entity_attribute, 'metadata'))
        self.assertEqual(entity_attribute.value, False)
        self.assertEqual(entity_attribute.type, 'boolean')

    def test_entity_attribute_int(self):
        entity_attribute = EntityAttribute(1, False)
        self.assertEqual(entity_attribute.metadata,
                         dict(python=dict(type='dataType',
                                          value='int'
                                          )
                              )
                         )
        self.assertEqual(entity_attribute.value, 1)
        self.assertEqual(entity_attribute.type, 'number')

    def test_entity_attribute_float(self):
        entity_attribute = EntityAttribute(2.132, False)
        self.assertEqual(entity_attribute.metadata,
                         dict(python=dict(type='dataType',
                                          value='float'
                                          )
                              )
                         )
        self.assertEqual(entity_attribute.value, 2.132)
        self.assertEqual(entity_attribute.type, 'number')

    def test_entity_attribute_long(self):
        # Evaluates to Long in Python 2
        entity_attribute = EntityAttribute(123456789123456789123456789, False)
        if sys.version_info <= (3, 0):
            self.assertEqual(entity_attribute.metadata,
                             dict(python=dict(type='dataType',
                                              value='long'
                                              )
                                  )
                             )
        else:
            self.assertEqual(entity_attribute.metadata,
                             dict(python=dict(type='dataType',
                                              value='int'
                                              )
                                  )
                             )
        self.assertEqual(entity_attribute.value, 123456789123456789123456789)
        self.assertEqual(entity_attribute.type, 'number')

    def test_entity_attribute_complex(self):
        entity_attribute = EntityAttribute(complex(3, 1), False)
        self.assertEqual(entity_attribute.metadata,
                         dict(python=dict(type='dataType',
                                          value='complex'
                                          )
                              )
                         )
        self.assertEqual(entity_attribute.value[0].value, 3)
        self.assertEqual(entity_attribute.value[1].value, 1)
        self.assertEqual(entity_attribute.type, 'array')

        entity_attribute = EntityAttribute(2.34j, False)
        self.assertEqual(entity_attribute.metadata,
                         dict(python=dict(type='dataType',
                                          value='complex'
                                          )
                              )
                         )
        self.assertEqual(entity_attribute.value[0].value, 0)
        self.assertEqual(entity_attribute.value[1].value, 2.34)
        self.assertEqual(entity_attribute.type, 'array')

    def test_entity_attribute_string(self):
        entity_attribute = EntityAttribute('Hello world!', False)
        self.assertTrue(not hasattr(entity_attribute, 'metadata'))
        self.assertEqual(entity_attribute.value, 'Hello world!')
        self.assertEqual(entity_attribute.type, 'string')

    def test_entity_attribute_unicode(self):
        entity_attribute = EntityAttribute(u'Unicode', False)
        # Python2 distinguishes between str and unicode
        if sys.version_info <= (3, 0):
            self.assertEqual(entity_attribute.metadata,
                             dict(python=dict(type='dataType',
                                              value='unicode'
                                              )
                                  )
                             )
        self.assertEqual(entity_attribute.value, u'Unicode')
        self.assertEqual(entity_attribute.type, 'string')

    def test_entity_attribute_tuple(self):
        entity_attribute = EntityAttribute((1, 2), False)
        self.assertEqual(entity_attribute.metadata,
                         dict(python=dict(type='dataType',
                                          value='tuple'
                                          )
                              )
                         )
        self.assertTrue(isinstance(entity_attribute.value, list))
        self.assertEqual(entity_attribute.value[0].value, 1)
        self.assertEqual(entity_attribute.value[1].value, 2)
        self.assertEqual(entity_attribute.type, 'array')

    def test_entity_attribute_list(self):
        entity_attribute = EntityAttribute([1, 2], False)
        self.assertTrue(not hasattr(entity_attribute, 'metadata'))
        self.assertTrue(isinstance(entity_attribute.value, list))
        self.assertEqual(entity_attribute.value[0].value, 1)
        self.assertEqual(entity_attribute.value[1].value, 2)
        self.assertEqual(entity_attribute.type, 'array')

    def test_entity_attribute_dict(self):
        entity_attribute = EntityAttribute(dict(a=1, b=2), False)
        self.assertTrue(not hasattr(entity_attribute, 'metadata'))
        self.assertTrue(isinstance(entity_attribute.value, dict))
        self.assertEqual(entity_attribute.value.get('a').value, 1)
        self.assertEqual(entity_attribute.value.get('b').value, 2)
        self.assertEqual(entity_attribute.type, 'object')

    def test_entity_attribute_foreign_class(self):
        entity_attribute = EntityAttribute(ClassInt(), False)
        self.assertEqual(entity_attribute.metadata,
                         dict(python=dict(type='dataType',
                                          value='class'
                                          )
                              )
                         )
        self.assertEqual(entity_attribute.type, 'ClassInt')
        self.assertTrue(entity_attribute.value is not None)

    def test_entity_attribute_complex_ignore_meta_data_true(self):
        entity_attribute = EntityAttribute(complex(3, 1), True)
        self.assertTrue(not hasattr(entity_attribute, 'metadata'))
        self.assertEqual(entity_attribute.value[0].value, 3)
        self.assertEqual(entity_attribute.value[1].value, 1)
        self.assertEqual(entity_attribute.type, 'array')

    def test_entity_attribute_float32_list_concrete_data_type(self):
        entity_attribute = EntityAttribute(ClassInt(),
                                           True,
                                           concreteDataType=dict(
                                               int='uint32_t'),
                                           baseEntity=True)
        self.assertTrue(hasattr(entity_attribute, 'metadata'))
        self.assertEqual(entity_attribute.metadata,
                         dict(dataType=dict(type='dataType',
                                            value=dict(int='uint32_t')
                                            )
                              )
                         )
        self.assertEqual(entity_attribute.value['int'].value, 1)
        self.assertEqual(entity_attribute.type, 'ClassInt')

    def test_entity_attribute_foreign_ros_class(self):
        entity_attribute = EntityAttribute(RosClassWithSlotsInt(), False)
        self.assertEqual(entity_attribute.metadata,
                         dict(python=dict(type='dataType',
                                          value='class'
                                          )
                              )
                         )
        # FOC should not touch it unless we encode!
        self.assertEqual(entity_attribute.type, 'RosClass/Integer')
        self.assertTrue(entity_attribute.value is not None)

    def test_entity_attribute_foreign_ros_class_encoded(self):
        entity_attribute = EntityAttribute(
            RosClassWithSlotsInt(), False, encode=True)
        self.assertEqual(entity_attribute.metadata,
                         dict(python=dict(type='dataType',
                                          value='class'
                                          )
                              )
                         )
        # FOC should encode it
        self.assertEqual(entity_attribute.type, 'RosClass%2FInteger')
        self.assertTrue(entity_attribute.value is not None)


class ComplexExample(object):
    def __init__(self):
        self.test_none = None
        self.test_bool = True
        self.test_int = 42
        self.test_float = 1.234
        self.test_complex = 42.42j
        self.test_str = 'I am a String'
        self.test_unicode = u'I am Unicode'
        self.test_tuple = (43, 2.345, ('Tuple', u' in tuple'))
        self.test_list = [44, 3.456, ['1', 2]]
        self.test_dict = dict(a=1, b=2.5j)
        self.test_class_int = ClassInt()
        self.test_class_int = [ClassInt()]*10  # Test id Array is supported
        self.test_class_int = ClassSlotsInt()
        # Test id Array is supported
        self.test_class_int = [ClassSlotsInt()]*10

    @classmethod
    def _complex_handler(cls, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            raise TypeError('Test Type-Error')

    @classmethod
    def to_json(cls, obj, ind=0):
        return json.dumps(obj.__dict__, default=cls._complex_handler, indent=ind)


class ClassInt():
    def __init__(self):
        self.int = 1


class ClassSlotsInt(object):
    __slots__ = ['val1']

    def __init__(self):
        self.val1 = 1


class RosClassWithSlotsInt(object):
    __slots__ = ['val1', '_type']
    _slot_types = ['uint8', 'string']

    def __init__(self):
        self.val1 = 1
        self._type = 'RosClass/Integer'  # Example-Type
