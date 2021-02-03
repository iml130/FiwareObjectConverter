# python class --> foc(python class) --> ngsi v2 --> json string --> ngsi-ld

class V2_Normalizer:
    @classmethod
    def _ngsiv2_uri(cls, ld_uri):
        return ld_uri.split('urn:ngsi-ld:')[1]

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
            out[key] = {}
            v2_attr = out[key]

            if not('type' in attr) or attr['type'] != 'Relationship':
                v2_attr['type'] = 'Property'
                v2_attr['value'] = attr['value']
            else:
                ref_key = 'ref'+str(key)
                v2_attr = out[ref_key]
                v2_attr['type'] = 'Reference'
                aux_obj = attr['object']
                if isinstance(aux_obj, list):
                    v2_attr['value'] = list()
                    for obj in aux_obj:
                        v2_attr['value'].append(cls._v2_object(obj))
                else:
                    v2_attr['value'] = cls._v2_object(str(aux_obj))

            #if key == 'location':
            #    ld_attr['type'] = 'GeoProperty'
            #
            #if 'type' in attr and attr['type'] == 'DateTime':
            #    ld_attr['value'] = {
            #        '@type': 'DateTime',
            #        '@value': normalize_date(attr['value'])
            #    }
            #
            #if 'type' in attr and attr['type'] == 'PostalAddress':
            #    ld_attr['value']['type'] = 'PostalAddress'

            if len(attr)>2:
                v2_attr['metadata'] = {}
                for mkey in attr:
                    if mkey not in ('type', 'value'):
                        sub_attr = dict()
                        sub_attr['type'] = 'Property'
                        sub_attr['value'] = attr[mkey]['value']
                        v2_attr['metadata'][mkey] = sub_attr
        return out


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
