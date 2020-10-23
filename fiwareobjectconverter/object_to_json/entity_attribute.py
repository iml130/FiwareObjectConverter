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
import array
import base64

try:
    import urllib.parse as quote
except ImportError:
    import urllib as quote

# TODO DL Threshold for converting large Arrays in ROS-Messages?
THRESH = 256


class EntityAttribute():
    """ Here the actual Conversion to the correct JSON-Format happens
    (no string is generated here). By initializing this class the given Object is
    translated into the format. This is straight-forward if-then-else-magic.
    Additional information are given for some types, for a bidirectional Conversion.

    """
    python_version = sys.version_info

    def __init__(self, _object, ipmd, concreteDataType=None, baseEntity=False, encode=False):
        self.value = _object
        self.type = ""
        self.metadata = dict()
        if baseEntity:
            self.set_concrete_meta_data(concreteDataType)
        object_type = type(_object)

        # Simply if-then-else to the Json fromat
        if object_type is type(None):
            pass
        elif object_type is bool:
            self.type = "boolean"
            self.value = bool(_object)
            # self.setConcreteMetaData(concreteDataType)
        elif object_type is int:
            self.type = "number"
            self.value = int(_object)
            self.set_python_meta_data(ipmd, "int")
            # self.setConcreteMetaData(concreteDataType)
        elif object_type is float:
            self.type = "number"
            self.value = float(_object)
            self.set_python_meta_data(ipmd, "float")
            # self.setConcreteMetaData(concreteDataType)
        # Check explicitly if Python 2 is used
        elif self.python_version < (3, 0) and object_type is long:
            self.type = "number"
            self.value = long(_object)
            self.set_python_meta_data(ipmd, "long")
            # self.setConcreteMetaData(concreteDataType)
        elif object_type is complex:
            self.type = "array"
            t = complex(_object)
            self.value = [EntityAttribute(
                t.real, ipmd), EntityAttribute(t.imag, ipmd)]
            self.set_python_meta_data(ipmd, "complex")
            # self.setConcreteMetaData(concreteDataType)
        elif object_type is str:
            # Thanks to ROS, Bytes are converted into
            self.type = "string"
            if not encode:
                self.value = str(_object)
            else:
                self.value = quote.quote(str(_object), safe='')

            # self.setConcreteMetaData(concreteDataType)
        # Check explicitly if Python 2 is used
        elif self.python_version < (3, 0) and object_type is unicode:
            self.type = "string"
            if not encode:
                self.value = unicode(_object)
            else:
                self.value = quote.quote(unicode(_object), safe='')
            # self.setConcreteMetaData(concreteDataType)
            self.set_python_meta_data(ipmd, "unicode")
        elif object_type is tuple:
            self.type = "array"
            self.value = []
            self.set_python_meta_data(ipmd, "tuple")
            self.set_concrete_meta_data(concreteDataType)
            for item in _object:
                self.value.append(EntityAttribute(item, ipmd, encode=encode))
        elif object_type is list:
            self.type = "array"
            self.value = []
            self.set_concrete_meta_data(concreteDataType)
            for item in _object:
                self.value.append(EntityAttribute(item, ipmd, encode=encode))
        elif object_type is dict:
            self.type = "object"
            temp_dict = {}
            for key, value in _object.items():
                inner_concrete_meta_data = None
                if concreteDataType is not None and key in concreteDataType:
                    inner_concrete_meta_data = concreteDataType[key]
                temp_dict[key] = EntityAttribute(
                    value, ipmd, inner_concrete_meta_data, encode=encode)
            self.value = temp_dict
        else:
            # Case it is a Class
            # check explicitly if it has the needed attrs
            if hasattr(_object, '__slots__'):
                iter_l = getattr(_object, '__slots__')
            elif hasattr(_object, '__dict__'):
                iter_l = _object.__dict__
            else:
                raise ValueError(
                    "Cannot get attrs from {}".format(str(_object)))

            # ROS-Specific Type-Declaration
            if hasattr(_object, '_type') and hasattr(_object, '_slot_types') and hasattr(_object, '__slots__'):
                # This is a special CASE for ROS!!!!
                if not encode:
                    self.type = _object._type
                else:
                    self.type = quote.quote(_object._type, safe='')

                self.set_python_meta_data(ipmd, "class")
                # Special Case 'Image-like'-Data in ROS (very long 'int8[]'- and 'uint8[]' - arrays)
                # These are converted into Base64 (escaped)
                temp_dict = {}
                for key, key_type in zip(_object.__slots__, _object._slot_types):
                    if key.startswith('_'):
                        continue
                    if ('int8[' in key_type or 'uint8[' in key_type) and len(getattr(_object, key)) >= THRESH:
                        # TODO DL 256 -> Threshold?
                        # Generate Base64 String of the Array:
                        temp_dict[key] = EntityAttribute(
                            None, ipmd, encode=encode)
                        temp_dict[key].type = "base64"

                        # Either generate unsigned or signed byte-array
                        if 'int8[' in key_type:
                            temp_dict[key].value = array.array(
                                'b', getattr(_object, key)).tostring()
                        else:
                            temp_dict[key].value = array.array(
                                'B', getattr(_object, key)).tostring()

                        # Form that Byte-Array: generate Base64 String
                        temp_dict[key].value = base64.b64encode(
                            temp_dict[key].value)

                        # Escape Special Characters:
                        temp_dict[key].value = quote.quote(
                            temp_dict[key].value, safe='')
                        temp_dict[key].metadata = dict()
                        self.set_concrete_meta_data(
                            concreteDataType[key], temp_dict[key])
                    else:
                        inner_concrete_meta_data = None
                        if concreteDataType is not None and key in concreteDataType:
                            # We have a special DatType for it
                            inner_concrete_meta_data = concreteDataType[key]
                            already_set = False  # Boolean to check if data ist already set
                            if "uint8[" in inner_concrete_meta_data:
                                # SPECIAL ROS CASE we have uint8[]-Array as a String or byte
                                # See: http://wiki.ros.org/msg#Fields -> Array-Handling
                                strange_obj = getattr(_object, key)
                                to_convert = None
                                if isinstance(strange_obj, str):
                                    # Looks like ROS converted it for us into str!
                                    to_convert = array.array(
                                        "B", strange_obj).tolist()
                                if not self.python_version < (3, 0) and isinstance(strange_obj, bytes):
                                    # Looks like ROS converted it for us into bytes!
                                    to_convert = list(strange_obj)
                                if to_convert is not None and len(to_convert) >= THRESH:
                                    # TODO DL 256 -> Threshold?
                                    # Generate Base64 String of the Array:
                                    temp_dict[key] = EntityAttribute(
                                        None, ipmd, encode=encode)
                                    temp_dict[key].type = "base64"

                                    # Generate unsigned or byte-array
                                    temp_dict[key].value = array.array(
                                        'B', getattr(_object, key)).tostring()

                                    # Form that Byte-Array: generate Base64 String
                                    temp_dict[key].value = base64.b64encode(
                                        temp_dict[key].value)

                                    # Escape Special Characters:
                                    temp_dict[key].value = quote.quote(
                                        temp_dict[key].value, safe='')
                                    temp_dict[key].metadata = dict()
                                    self.set_concrete_meta_data(
                                        inner_concrete_meta_data, temp_dict[key])
                                    already_set = True

                            else:
                                # Something else we should convert
                                to_convert = getattr(_object, key)
                            if already_set is False:
                                temp_dict[key] = EntityAttribute(
                                    to_convert, ipmd, inner_concrete_meta_data, encode=encode)
                        else:
                            # Just get its child and convert it
                            temp_dict[key] = EntityAttribute(
                                getattr(_object, key), ipmd, None, encode=encode)
                self.value = temp_dict
            else:
                # Simple Class. Recursively retrieve the other values
                self.type = _object.__class__.__name__
                self.set_python_meta_data(ipmd, "class")
                temp_dict = {}
                for key in iter_l:
                    if key.startswith('_'):
                        continue
                    inner_concrete_meta_data = None
                    if concreteDataType is not None and key in concreteDataType:
                        inner_concrete_meta_data = concreteDataType[key]
                    temp_dict[key] = EntityAttribute(
                        getattr(_object, key), ipmd, inner_concrete_meta_data, encode=encode)
                self.value = temp_dict

        # Remove metadata-Attribute if it is empty (minimizing the JSON)
        if self.metadata == {}:
            delattr(self, "metadata")

    def set_python_meta_data(self, ignore_python_meta_data, val):
        if not ignore_python_meta_data:
            self.metadata["python"] = dict(type="dataType", value=val)

    def set_concrete_meta_data(self, val, obj=None):
        if val is not None and obj is None:
            self.metadata["dataType"] = dict(type="dataType", value=val)
        elif val is not None:
            obj.metadata["dataType"] = dict(type="dataType", value=val)
