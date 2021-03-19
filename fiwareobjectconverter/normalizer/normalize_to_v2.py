# python class --> foc(python class) --> ngsi v2 --> json string --> ngsi-ld

class V2_Normalizer:
    @classmethod
    def _ngsiv2_uri(cls, ld_uri):
        ld_uri = ld_uri.split('urn:ngsi-ld:')[1]
        return ld_uri.split(':')[1]

    @classmethod
    # Generates a Relationship's object as a URI
    def _v2_object(cls, ld_uri):
        return cls._ngsiv2_uri(ld_uri)

    @classmethod
    # Do all the transformation work
    def _normalized_2_v2(cls, entity):
        out = {}
        for key in entity:
            if key == '@context':
                continue

            if key == 'id':
                out[key] = cls._ngsiv2_uri(entity['id'])
                continue

            if key == 'type':
                out[key] = entity[key]
                continue

            if key == 'createdAt':
                out['dateCreated'] = cls._normalize_date(entity[key]['value'])
                continue

            if key == 'modifiedAt':
                out['dateModified'] = cls._normalize_date(entity[key]['value'])
                continue

            attr = entity[key]
            out[key] = cls._normalize_attribute(key, attr)
        return out

    @classmethod
    def _normalize_attribute(cls, key, attr):
        v2_attr = {}
        if not('type' in attr) or attr['type'] != 'Relationship':
            if key == 'python':
                v2_attr['type'] = 'dataType'
            else:
                obj_ = attr['value']
                if isinstance(obj_, str):
                    type_ = 'string'
                elif isinstance(obj_, bool):
                    type_ = 'boolean'
                elif isinstance(obj_, int):
                    type_ = 'number'
                elif isinstance(obj_, float):
                    type_ = 'number'
                elif isinstance(obj_, complex):
                    type_ = 'array'
                elif isinstance(obj_, tuple):
                    type_ = 'array'
                elif isinstance(obj_, list):
                    type_ = 'array'
                elif isinstance(obj_, dict):
                    if 'type' in obj_.keys():
                        type_ = obj_['type']
                    else:
                        type_ = 'object'
                else:
                    if obj_['type']:
                        type_ = obj_['type']
                    else:
                        type_ = 'object'
                v2_attr['type'] = type_

            if v2_attr['type'] in ['string', 'number', 'boolean']:
                v2_attr['value'] = attr['value']
            elif v2_attr['type'] == 'array':
                v2_attr['value'] = []
                obj_attr = attr['value']
                for new_key in obj_attr:
                    v2_attr['value'].append(
                        cls._normalize_attribute(None, new_key))
            else:
                v2_attr['value'] = {}
                com_attr = attr['value']
                for new_key in com_attr:
                    if new_key != 'type':
                        v2_attr['value'][new_key] = cls._normalize_attribute(
                            new_key, com_attr[new_key])
        else:
            #ref_key = 'ref'+str(key)
            #v2_attr = out[ref_key]
            v2_attr['type'] = 'Reference'
            aux_obj = attr['object']
            if isinstance(aux_obj, list):
                v2_attr['value'] = list()
                for obj in aux_obj:
                    v2_attr['value'].append(cls._v2_object(obj))
            else:
                v2_attr['value'] = cls._v2_object(str(aux_obj))

        # if key == 'location':
        #    ld_attr['type'] = 'GeoProperty'
        #
        # if 'type' in attr and attr['type'] == 'DateTime':
        #    ld_attr['value'] = {
        #        '@type': 'DateTime',
        #        '@value': normalize_date(attr['value'])
        #    }
        #
        # if 'type' in attr and attr['type'] == 'PostalAddress':
        #    ld_attr['value']['type'] = 'PostalAddress'

        if len(attr) > 2:
            metadata = {}
            for mkey in attr:
                if mkey == 'v2_type':
                    continue
                if mkey not in ('type', 'value'):
                    sub_attr = dict()
                    sub_attr['type'] = 'dataType'
                    sub_attr['value'] = attr[mkey]['value']
                    metadata[mkey] = sub_attr
            if len(metadata) > 0:
                v2_attr['metadata'] = metadata
        return v2_attr

    @classmethod
    def _normalize_date(cls, date_str):
        out = date_str

        if date_str.endswith('Z'):
            out = out[:-1]

        return out

    @classmethod
    def normalize(cls, input_):
        result = cls._normalized_2_v2(input_)
        return result
