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
from fiwareobjectconverter.object_fiware_converter import ObjectFiwareConverter


class TestJsonConverter(unittest.TestCase):

    def test_to_fiware(self):
        ObjectFiwareConverter.obj_to_fiware(TestClass(), indent=4)

    def test_to_obj(self):
        test_to_obj = """
                        {
                            "type": "TestClass",
                            "id": "TestClass1",
                            "val":  {
                                        "type": "number",
                                        "value": 1,
                                        "metadata": {}
                                    }
                        }
                        """
        test_class = TestClass()
        # Evaluates automatically to Long for Python 2
        test_class.val = 123456789123456789123456789
        ObjectFiwareConverter.fiware_to_obj(test_to_obj, test_class)
        self.assertEqual(test_class.val, 1)

    def test_to_obj_without_metadata_unicode(self):
        json = """
                {
                    "type": "TestClass",
                    "id": "ID",
                    "val":  {
                                "type": "string",
                                "value":"i am unicode",
                                "metadata": {
                                                "python":   {
                                                                "type":"dataType",
                                                                "value":"unicode"
                                                            }
                                            }
                            }
                }
                """
        test_class = TestClass()
        test_class.val = str(' ')
        ObjectFiwareConverter.fiware_to_obj(
            json, test_class, use_meta_data=False)
        self.assertEqual(type(test_class.val), str)
        self.assertEqual(test_class.val, 'i am unicode')  # Not unicode

    def test_to_object_without_meta_data_and_type_check_unicode(self):
        json = """
                {
                    "type":"TestClass",
                    "id":"ID",
                    "val":  {
                                "type":"string",
                                "value":"i am unicode",
                                "metadata": {
                                                "python":   {
                                                                "type":"dataType",
                                                                "value":"unicode"
                                                            }
                                            }
                            }
                }
                """
        test_class = TestClass()
        ObjectFiwareConverter.fiware_to_obj(
            json, test_class, use_meta_data=False, ignore_wrong_data_type=True)
        self.assertEqual(type(test_class.val), str)
        self.assertEqual(test_class.val, 'i am unicode')  # Not unicode

    def test_to_object_without_meta_data_complex(self):
        json = """
                {
                    "type": "TestClass",
                    "id": "ID",
                    "val":  {
                                "type": "array",
                                "value": [  {
                                                "type": "number",
                                                "value": 0.0,
                                                "metadata": {
                                                                "python":   {
                                                                              "type": "dataType",
                                                                              "value": "float"
                                                                            }
                                                            }
                                            },
                                            {
                                                "type": "number",
                                                "value": 2.1,
                                                "metadata": {
                                                                "python":   {
                                                                              "type": "dataType",
                                                                              "value": "float"
                                                                            }
                                                            }
                                            }
                                         ],
                                "metadata": {
                                                "python":   {
                                                                "type": "dataType",
                                                                "value": "complex"
                                                            }
                                            }
                            }
                }
                """
        test_class = TestClass()
        test_class.val = list()
        ObjectFiwareConverter.fiware_to_obj(
            json, test_class, use_meta_data=False)
        self.assertEqual(type(test_class.val), list)
        self.assertEqual(test_class.val, [0, 2.1])  # Not unicode

    def test_to_fiware_to_object(self):
        json = ObjectFiwareConverter.obj_to_fiware(TestClass())

        test_class = TestClass()
        test_class.val = 42
        ObjectFiwareConverter.fiware_to_obj(json, test_class)

        self.assertEqual(test_class.val, 1)

    def test_to_fiware_to_object_without_id_value(self):
        json = ObjectFiwareConverter.obj_to_fiware(
            TestClass(), show_id_value=False)

        test_class = TestClass()
        test_class.val = 42
        ObjectFiwareConverter.fiware_to_obj(json, test_class)

        self.assertEqual(test_class.val, 1)

    def test_integer_type(self):  # TODO Accept Integers and other primitives?
        json = """{"id":"Task1","type":"Task","task":{"type":"Integer","value":0}}"""
        test_class = TestClass()
        test_class.val = 1  # set Number/Integer

        ObjectFiwareConverter.fiware_to_obj(json, test_class, set_attr=True)

        self.assertEqual(getattr(test_class, 'task'), 0)
        self.assertEqual(getattr(test_class, 'id'), 'Task1')
        self.assertEqual(getattr(test_class, 'type'), 'Task')
        self.assertEqual(test_class.val, 1)


class TestClass(object):
    def __init__(self):
        self.val = 1
