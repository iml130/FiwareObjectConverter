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
from fiwareobjectconverter.object_to_json.entity import Entity


class TestJsonConverter(unittest.TestCase):

    def test_entity_initialize_is_not_empty(self):
        entity = Entity()
        self.assertEqual(entity.type, 'Entity')
        self.assertEqual(entity.id[0:6], 'Entity')

    def test_entity_set_object_primitive(self):
        entity = Entity()
        try:
            entity.set_object(1, {}, False)
        except ValueError:
            self.assertTrue(True)

    def test_entity_set_object_non_primitive(self):
        entity = Entity()
        entity.set_object(TestClass(), {}, False)
        self.assertEqual(entity.id[0:9], 'TestClass')
        self.assertEqual(entity.type, 'TestClass')
        self.assertEqual(entity.__dict__['value'].value, 1)

    def test_entity_set_object_non_primitive_with_given_type_id(self):
        entity = Entity()
        entity.set_object(TypeIDTestClass(), {}, False)
        self.assertEqual(entity.id[0:9], 'MyId')
        self.assertEqual(entity.type, 'This should NOT be overwritten')
        self.assertEqual(entity.__dict__['value'].value, 1)

    def test_entity_set_object_non_primitive_without_type_id(self):
        entity = Entity()
        entity.set_object(TestClass(), {}, False, show_id_value=False)
        self.assertFalse(hasattr(entity, 'id'))
        self.assertFalse(hasattr(entity, 'type'))
        self.assertEqual(entity.__dict__['value'].value, 1)


class TestClass(object):
    def __init__(self):
        self.value = 1


class TypeIDTestClass(object):
    def __init__(self):
        self.value = 1
        self.type = 'This should NOT be overwritten'    # Needed behaviour, so that the
                                                        # user can decide the type and id

        self.id = 'MyId'
