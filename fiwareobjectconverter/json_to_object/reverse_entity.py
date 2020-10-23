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

try:
    import urllib.parse as quote
except ImportError:
    import urllib as quote
from fiwareobjectconverter.json_to_object.reverse_entity_attribute import ReverseEntityAttribute

MISMATCH_MESSAGE = "The Class-Type does not match with the JSON-type ({} != {})"


class ReverseEntity(object):
    """ A simple class which reconverts from JSON into a __dict__.
        The Function setObject decides if type check (ignoreWrongDataType)
        is used and adds the (if the key from JSON is also in obj) value to the obj.
        'setAttr' is here explicitly used, if set to true.
    """

    def __init__(self, type_var=None, id_var=None, *args, **payload):
        self.type = type_var
        self.id_var = id_var
        self.payload = payload

    def set_object(self, obj, use_meta_data=True, ignore_wrong_data_type=False,
                    set_attr=False, encoded=False):
        # Explicitly set id and type, always!
        if encoded:
            setattr(obj, 'id', str(self.id_var))
            setattr(obj, 'type', str(self.type))
        else:
            setattr(obj, 'id', quote.unquote(str(self.id_var)))
            setattr(obj, 'type', quote.unquote(str(self.type)))



        for key, value in self.payload.items():
            rea = ReverseEntityAttribute(value, use_meta_data, encoded=encoded)
            if set_attr:
                # Just use setAttr
                setattr(obj, key, rea.get_value())
            elif key in obj.__dict__:
                if ignore_wrong_data_type:
                    # Ignoring expected Data-Type
                    obj.__dict__[key] = rea.get_value()
                else:
                    val = rea.get_value()
                    if type(obj.__dict__[key]) is not type(val):
                        raise TypeError(MISMATCH_MESSAGE.format(type(obj.__dict__[key]), type(val)))
                    else:
                        obj.__dict__[key] = val
