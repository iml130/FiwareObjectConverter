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
            self.setConcreteMetaData(concreteDataType)
        objectType = type(_object)

        # Simply if-then-else to the Json fromat
        if(objectType is type(None)):
            pass
        elif objectType is bool:
            self.type = "boolean"
            self.value = bool(_object)
            # self.setConcreteMetaData(concreteDataType)
        elif objectType is int:
            self.type = "number"
            self.value = int(_object)
            self.setPythonMetaData(ipmd, "int")
            # self.setConcreteMetaData(concreteDataType)
        elif objectType is float:
            self.type = "number"
            self.value = float(_object)
            self.setPythonMetaData(ipmd, "float")
            # self.setConcreteMetaData(concreteDataType)
        # Check explicitly if Python 2 is used
        elif self.python_version < (3, 0) and objectType is long:
            self.type = "number"
            self.value = long(_object)
            self.setPythonMetaData(ipmd, "long")
            # self.setConcreteMetaData(concreteDataType)
        elif objectType is complex:
            self.type = "array"
            t = complex(_object)
            self.value = [EntityAttribute(
                t.real, ipmd), EntityAttribute(t.imag, ipmd)]
            self.setPythonMetaData(ipmd, "complex")
            # self.setConcreteMetaData(concreteDataType)
        elif objectType is str:
            # Thanks to ROS, Bytes are converted into
            self.type = "string"
            if not encode:
                self.value = str(_object)
            else:
                self.value = quote.quote(str(_object), safe='')

            # self.setConcreteMetaData(concreteDataType)
        # Check explicitly if Python 2 is used
        elif self.python_version < (3, 0) and objectType is unicode:
            self.type = "string"
            if not encode:
                self.value = unicode(_object)
            else:
                self.value = quote.quote(unicode(_object), safe='')
            # self.setConcreteMetaData(concreteDataType)
            self.setPythonMetaData(ipmd, "unicode")
        elif objectType is tuple:
            self.type = "array"
            self.value = []
            self.setPythonMetaData(ipmd, "tuple")
            self.setConcreteMetaData(concreteDataType)
            for item in _object:
                self.value.append(EntityAttribute(item, ipmd, encode=encode))
        elif objectType is list:
            self.type = "array"
            self.value = []
            self.setConcreteMetaData(concreteDataType)
            for item in _object:
                self.value.append(EntityAttribute(item, ipmd, encode=encode))
        elif objectType is dict:
            self.type = "object"
            tempDict = {}
            for key, value in _object.items():
                innerConcreteMetaData = None
                if concreteDataType is not None and key in concreteDataType:
                    innerConcreteMetaData = concreteDataType[key]
                tempDict[key] = EntityAttribute(
                    value, ipmd, innerConcreteMetaData, encode=encode)
            self.value = tempDict
        else:
            # Case it is a Class
            # check explicitly if it has the needed attrs
            if (hasattr(_object, '__slots__')):
                iterL = getattr(_object, '__slots__')
            elif(hasattr(_object, '__dict__')):
                iterL = _object.__dict__
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

                self.setPythonMetaData(ipmd, "class")
                # Special Case 'Image-like'-Data in ROS (very long 'int8[]'- and 'uint8[]' - arrays)
                # These are converted into Base64 (escaped)
                tempDict = {}
                for key, key_type in zip(_object.__slots__, _object._slot_types):
                    if key.startswith('_'):
                        continue
                    if ('int8[' in key_type or 'uint8[' in key_type) and len(getattr(_object, key)) >= THRESH:
                        # TODO DL 256 -> Threshold?
                        # Generate Base64 String of the Array:
                        tempDict[key] = EntityAttribute(
                            None, ipmd, encode=encode)
                        tempDict[key].type = "base64"

                        # Either generate unsigned or signed byte-array
                        if 'int8[' in key_type:
                            tempDict[key].value = array.array(
                                'b', getattr(_object, key)).tostring()
                        else:
                            tempDict[key].value = array.array(
                                'B', getattr(_object, key)).tostring()

                        # Form that Byte-Array: generate Base64 String
                        tempDict[key].value = base64.b64encode(
                            tempDict[key].value)

                        # Escape Special Characters:
                        tempDict[key].value = quote.quote(
                            tempDict[key].value, safe='')
                        tempDict[key].metadata = dict()
                        self.setConcreteMetaData(
                            concreteDataType[key], tempDict[key])
                    else:
                        innerConcreteMetaData = None
                        if concreteDataType is not None and key in concreteDataType:
                            # We have a special DatType for it
                            innerConcreteMetaData = concreteDataType[key]
                            alreadySet = False  # Boolean to check if data ist already set
                            if "uint8[" in innerConcreteMetaData:
                                # SPECIAL ROS CASE we have uint8[]-Array as a String or byte
                                # See: http://wiki.ros.org/msg#Fields -> Array-Handling
                                strangeObj = getattr(_object, key)
                                toConvert = None
                                if type(strangeObj) is str:
                                    # Looks like ROS converted it for us into str!
                                    toConvert = array.array(
                                        "B", strangeObj).tolist()
                                if not self.python_version < (3, 0) and type(strangeObj) is bytes:
                                    # Looks like ROS converted it for us into bytes!
                                    toConvert = list(strangeObj)
                                if toConvert is not None and len(toConvert) >= THRESH:
                                    # TODO DL 256 -> Threshold?
                                    # Generate Base64 String of the Array:
                                    tempDict[key] = EntityAttribute(
                                        None, ipmd, encode=encode)
                                    tempDict[key].type = "base64"

                                    # Generate unsigned or byte-array
                                    tempDict[key].value = array.array(
                                        'B', getattr(_object, key)).tostring()

                                    # Form that Byte-Array: generate Base64 String
                                    tempDict[key].value = base64.b64encode(
                                        tempDict[key].value)

                                    # Escape Special Characters:
                                    tempDict[key].value = quote.quote(
                                        tempDict[key].value, safe='')
                                    tempDict[key].metadata = dict()
                                    self.setConcreteMetaData(
                                        innerConcreteMetaData, tempDict[key])
                                    alreadySet = True

                            else:
                                # Something else we should convert
                                toConvert = getattr(_object, key)
                            if alreadySet is False:
                                tempDict[key] = EntityAttribute(
                                    toConvert, ipmd, innerConcreteMetaData, encode=encode)
                        else:
                            # Just get its child and convert it
                            tempDict[key] = EntityAttribute(
                                getattr(_object, key), ipmd, None, encode=encode)
                self.value = tempDict
            else:
                # Simple Class. Recursively retrieve the other values
                self.type = _object.__class__.__name__
                self.setPythonMetaData(ipmd, "class")
                tempDict = {}
                for key in iterL:
                    if key.startswith('_'):
                        continue
                    innerConcreteMetaData = None
                    if concreteDataType is not None and key in concreteDataType:
                        innerConcreteMetaData = concreteDataType[key]
                    tempDict[key] = EntityAttribute(
                        getattr(_object, key), ipmd, innerConcreteMetaData, encode=encode)
                self.value = tempDict

        # Remove metadata-Attribute if it is empty (minimizing the JSON)
        if self.metadata == {}:
            delattr(self, "metadata")

    def setPythonMetaData(self, ignorePythonMetaData, val):
        if not ignorePythonMetaData:
            self.metadata["python"] = dict(type="dataType", value=val)

    def setConcreteMetaData(self, val, obj=None):
        if val is not None and obj is None:
            self.metadata["dataType"] = dict(type="dataType", value=val)
        elif val is not None:
            obj.metadata["dataType"] = dict(type="dataType", value=val)
