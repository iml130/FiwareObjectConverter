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

import base64
import array
try:
    import urllib.parse as quote
except ImportError:
    import urllib as quote


# Error Messages
TYPE_VALUE_METADATA_NOT_DEFINED_MESSAGE = 'One of the following is not defined in json: {type|value}'
VALUE_EMPTY_MESSAGE = 'The Value entered cannot be empty!'

# Types which can be retrieved from the JSON:
NUMERICAL_TYPES = ['number', 'integer', 'int', 'float', 'double', 'long', ]
TEXT_TYPES = ['string',  'text']
BOOLEAN_TYPES = ['bool',  'boolean']
ARRAYLIKE_TYPES = ['array', 'list', 'tuple', 'vector']
OBJECTLIKE_TYPES = ['object', 'obj']
try:
    # Python 2
    WHOLE_NUMBERS = [int, long]
    STRING_TYPES = [unicode, str]
    COMPLEX_TYPES = [complex, tuple, list]
except NameError:
    # Python 3
    WHOLE_NUMBERS = [int]
    STRING_TYPES = [str]
    COMPLEX_TYPES = [complex, tuple, list]


class ReverseEntityAttribute(object):
    """ Here the actual Conversion happens.
        By initiliazing the class, the _dict is translated into the
        primitive datatypes. With the variable useMetaData the metadata can be ignored
        It defaults then from:
        Complex, Tuple -> List
        Unicode -> String
    """

    def __init__(self, _dict, useMetaData=True, encoded=False):
        """ By initializing we set the value in self.value
        """
        self.value = None

        if _dict is None:
            raise ValueError(VALUE_EMPTY_MESSAGE)

        if 'type' not in _dict or 'value' not in _dict:
            # Check if a correct struct exists.
            raise ValueError(TYPE_VALUE_METADATA_NOT_DEFINED_MESSAGE)

        if not 'metadata' in _dict:
            useMetaData = False

        if encoded:
            _dict['type'] = quote.unquote(_dict['type'])

        # Back Conversion:
        if _dict['type'] == '':
            self.value = _dict['value']

        elif _dict['type'].lower() in BOOLEAN_TYPES:
            self._set_value(bool, _dict['value'])

        elif _dict['type'].lower() in NUMERICAL_TYPES:
            # Case something numerical
            self._set_value(float, _dict['value'])
            if self.value % 1 == 0.0:
                # Number is Integer Like, convert to int or long
                self._set_value_with_metadata(
                    WHOLE_NUMBERS, useMetaData, _dict, self.value)

        elif _dict['type'].lower() in TEXT_TYPES:
            # Case String or Unicode
            self._set_value_with_metadata(
                STRING_TYPES, useMetaData, _dict, _dict['value'])
            if encoded:
                self.value = quote.unquote(self.value)

        elif _dict['type'].lower() in ARRAYLIKE_TYPES:
            # Case Complex, Tuple or List
            # First: reverse every element to Obj
            temp_list = _dict['value']
            temp_value = list()
            for value in temp_list:
                reverse_entity_attribute = ReverseEntityAttribute(value, useMetaData)
                temp_value.append(reverse_entity_attribute.get_value())

            # Second: decide if Complex, Tuple or List
            self._set_value_with_metadata(
                COMPLEX_TYPES, useMetaData, _dict, temp_value)

        elif _dict['type'].lower() in OBJECTLIKE_TYPES:
            # arbitary JSON object with key, value
            temp_dict = _dict['value']
            self.value = {}
            for key, value in temp_dict.items():
                rea = ReverseEntityAttribute(value, useMetaData)
                self.value[key] = rea.get_value()

        elif _dict['type'].lower() == 'base64':
            # Case we have a base64 String:
            # First Unquote Special Characters
            temp_value = quote.unquote(_dict['value'])

            # Decode Base64 String into Bytes
            temp_value = base64.b64decode(temp_value)

            # Retrieve Information about int8 or uint8
            if 'metadata' in _dict and 'dataType' in _dict['metadata']:
                datatype = _dict['metadata']['dataType']['value']
            else:
                raise ValueError(
                    'Unknown Object-Type: ' + _dict['type'] +
                     '. The MetaData does not specify what the actual DataType is.')

            # convert back to integers
            if datatype == 'int8[]':
                temp_value = array.array('b', temp_value)
            else:
                temp_value = array.array('B', temp_value)

            # Change DataType to primitive python list
            self.value = temp_value.tolist()

        else:
            # Maybe a class with key, value or another JSON object, check if you can iterate!
            if not hasattr(_dict['value'], 'items'):
                raise ValueError(
                    'Unknown Object-Type: ' + _dict['type'] +
                     '. And it is not possible to iterate over this Object-Type!')

            temp_dict = {}
            for key, value in _dict['value'].items():
                rea = ReverseEntityAttribute(value, useMetaData)
                temp_dict[key] = rea.get_value()
            self.value = temp_dict

    def get_value(self):
        return self.value

    def _set_value(self, target_type, value):
        """ This function sets self.value  .
            Complex needs to be called differently
            and we need to check if the input of bool is a string
        """
        if target_type == bool and isinstance(value, str):
            self.value = value.lower in ['false', 'f', '0']
        elif target_type != complex:
            self.value = target_type(value)
        else:
            self.value = target_type(*value)

    def _set_value_with_metadata(self, target_types, use_meta_data, readict, value):
        """ This function sets the Value, dependent on the given metadata.
            If no metadata is given or it does not contain the correct format,
            we default to the last element of targetTypes
        """
        if use_meta_data and 'python' in readict['metadata']:
            metadata = readict['metadata']

            # we try to find a valid dataType
            for target_type in target_types:
                if metadata['python'] == dict(type='dataType', value=target_type.__name__):
                    self._set_value(target_type, value)
                    return

            # Case: we did not set self.value, we default to the last element
            self._set_value(target_types[-1], value)
        else:
            # Case: no metadata, we also default to the last element
            self._set_value(target_types[-1], value)
