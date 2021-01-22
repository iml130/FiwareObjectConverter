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
    def obj_to_fiware(cls, object_, indent=0, data_type_dict=None, ignore_python_meta_data=False,
                      show_id_value=True, encode=False):
        """
        This method should be primarily used to convert a Object -> JSON-string.

        Parameters
        ----------
        object_ :
            The Object, which should be converted.
        ind : int
            <Desctription of ind>
        data_type_dict : dict
            <Desctription of data_type_dict>
        ignore_python_meta_data : bool
            <Desctription of ignore_python_meta_data>
        show_id_value : bool
            <Desctription of show_id_value>
        encode : bool
            <Desctription of encode>

        Returns
        -------
        xxx
            Returning value
        """
        if data_type_dict is None:
            data_type_dict = {}
        entity = Entity()
        entity.set_object(object_, data_type_dict, ignore_python_meta_data,
                          show_id_value=show_id_value, encode=encode)
        return cls._json(entity, indent)

    @classmethod
    def fiware_to_obj(cls, fiware_entity, object_structure=None, use_meta_data=True,
                      ignore_wrong_data_type=False, set_attr=False, encoded=False):
        """
        This method should be primarily used to convert a JSON-string -> Object.

        Parameters
        ----------
        fiware_entity :
            <Desctription of object_>
        object_structure : dict
            <Desctription of object_>
        use_meta_data : bool
            <Desctription of object_>
        ignore_wrong_data_type : bool
            <Desctription of object_>
        set_attr : bool
            <Desctription of object_>
        encoded : bool
            <Desctription of object_>

        Returns
        -------
        xxx
            Returning value
        """
        if object_structure is None:
            object_structure = {}
        json_obj = None
        if isinstance(fiware_entity, str):
            json_obj = cls._obj(fiware_entity)
        else:
            json_obj = fiware_entity
        reverse_entity = ReverseEntity(**json_obj)
        return reverse_entity.set_object(object_structure, use_meta_data, ignore_wrong_data_type,
                                         set_attr, encoded=encoded)

    @classmethod
    def _complex_handler(cls, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            raise TypeError('Object of type %s with value of %s is not JSON serializable' % (
                type(obj), repr(obj)))

    @classmethod
    def _json(cls, obj, indent=0):
        return json.dumps(obj.__dict__, default=cls._complex_handler, indent=indent)

    @classmethod
    def _obj(cls, json_str):
        return json.loads(json_str)
