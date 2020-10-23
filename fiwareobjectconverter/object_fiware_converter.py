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

""" This Module converts Python-Objects into the Fiware-JSON-Format.
    For more Information how to use this class, see the Readme.md
    You can find the needed Files to convert from an Object into JSON
    in the folder JsonToObject and vice versa
"""

import json
import sys
import os
from fiwareobjectconverter.object_to_json.entity import Entity
from fiwareobjectconverter.json_to_object.reverse_entity import ReverseEntity
# Adding This Sub-Project into the PythonPath
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


class ObjectFiwareConverter(object):
    """ This class should be primarily used to convert a Object <-> JSON-string.
        The classes in subdirectories are either used to convert them into JSON
        or into a Python-specific-Object.
    """

    @classmethod
    def obj_to_fiware(cls, _object, ind=0, data_type_dict={}, ignore_python_meta_data=False,
                        show_id_value=True, encode=False):
        entity = Entity()
        entity.set_object(_object, data_type_dict, ignore_python_meta_data,
                     show_id_value=show_id_value, encode=encode)
        return cls._json(entity, ind)

    @classmethod
    def fiware_to_obj(cls, _fiware_entity, _object_structure={}, use_meta_data=True,
                    ignore_wrong_data_type=False, set_attr=False, encoded=False):
        json_obj = None
        if isinstance(_fiware_entity, str):
            json_obj = cls._obj(_fiware_entity)
        else:
            json_obj = _fiware_entity
        reverse_entity = ReverseEntity(**json_obj)
        return reverse_entity.set_object(_object_structure, use_meta_data, ignore_wrong_data_type,
                                set_attr, encoded=encoded)

    @classmethod
    def _complex_handler(cls, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
                type(obj), repr(obj)))

    @classmethod
    def _json(cls, obj, ind=0):
        return json.dumps(obj.__dict__, default=cls._complex_handler, indent=ind)

    @classmethod
    def _obj(cls, json_str):
        return json.loads(json_str)
