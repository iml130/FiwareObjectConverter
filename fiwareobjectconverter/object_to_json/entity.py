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

""" This Module ...
"""

import uuid

try:
    import urllib.parse as quote
except ImportError:
    import urllib as quote

from fiwareobjectconverter.object_to_json.entity_attribute import EntityAttribute

ERROR_MESSAGE_ATTTRIBUTE = 'Error setting Object in \'setObject\' : '


class Entity(object):
    """ This is the Entity which will be later serialized with json.
        Here the __dict__ is set with setObject. Also the uuid is here generated and
        all types are converted into correct structure with EntityAttribute.
        The Keys "type" "id" and "_*" are ignored and not added into the Entity

    Attributes
    ----------
    type : str
        xxx
    id : str
        xxx
    """

    def __init__(self):
        self.type = self.__class__.__name__
        self.id = self.type + str(uuid.uuid4())


    def set_object(self, object_, data_type_dict, ignore_python_meta_data,
                   show_id_value=True, encode=False):
        """
        ...

        Parameters
        ----------
        object_ :
            The Object, which should be converted.
        data_type_dict : dict
            <Desctription of data_type_dict>
        ignore_python_meta_data : bool
            <Desctription of ignore_python_meta_data>
        show_id_value : bool
            <Desctription of show_id_value>
        encoded : bool
            <Desctription of encoded>

        Returns
        -------
        xxx
            Returning value
        """
        # Clear own dictionary
        self.__dict__.clear()
        try:
            if show_id_value:
                # Setting EntityType and EntitiyID
                self.type = object_.__class__.__name__
                self.id = self.type + str(uuid.uuid4())

            # Set Key/Value in own Dictionary
            if isinstance(object_, dict):
                iter_l = object_.keys()
            elif hasattr(object_, '__slots__'):
                iter_l = getattr(object_, '__slots__')
            else:
                iter_l = object_.__dict__

            for key in iter_l:
                # Explicitly set id and type if it exists
                if (key == 'id' and show_id_value):
                    if isinstance(object_, dict):
                        self.id = object_[key]
                    else:
                        self.id = getattr(object_, key)
                elif (key == 'type' and show_id_value):
                    if isinstance(object_, dict):
                        self.type = object_[key]
                    else:
                        self.type = getattr(object_, key)
                else:
                    if isinstance(object_, dict):
                        value = object_[key]
                    else:
                        value = getattr(object_, key)
                    if key.startswith('_', 0, 1):
                        # Object contains invalid key-name, ignore!
                        pass
                    else:
                        self.__dict__[key] = EntityAttribute(value, ignore_python_meta_data,
                                                             data_type_dict.get(key),
                                                             baseEntity=True, encode=encode)
        except AttributeError as ex:
            raise ValueError(ERROR_MESSAGE_ATTTRIBUTE, ex) from ex

        # Encode in HTML (OCB Specific!)
        if encode and show_id_value:
            self.type = quote.quote(self.type, safe='')
            self.id = quote.quote(self.id, safe='')

    def __repr__(self):
        return 'Id: ' + str(self.id) + ', Type: ' + str(self.type)
