# -*- coding: utf-8 -*-

from tournai.urban.dataimport.notaries.mappers import AddressMapper
from tournai.urban.dataimport.notaries.mappers import IdMapper
from tournai.urban.dataimport.notaries.mappers import NotaryFactory
from tournai.urban.dataimport.notaries.mappers import TitleMapper

from imio.urban.dataimport.mapper import SimpleMapper


OBJECTS_NESTING = [
    ('NOTARY', [],),
]

FIELDS_MAPPINGS = {
    'NOTARY':
    {
        'factory': [NotaryFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'NOM',
                    'to': 'name1',
                },
                {
                    'from': 'PRENOM',
                    'to': 'name2',
                },
                {
                    'from': 'CODE',
                    'to': 'zipcode',
                },
                {
                    'from': 'VILLE',
                    'to': 'city',
                },
                {
                    'from': 'Mail',
                    'to': 'email',
                },
                {
                    'from': 'TEL',
                    'to': 'phone',
                },
                {
                    'from': 'FAX',
                    'to': 'fax',
                },
            ),

            IdMapper: {
                'from': 'NOM',
                'to': 'id',
            },

            TitleMapper: {
                'from': 'TITRE',
                'to': 'personTitle',
            },

            AddressMapper: {
                'from': 'ADRESSE',
                'to': ('street', 'number')
            },
        },
    },
}
