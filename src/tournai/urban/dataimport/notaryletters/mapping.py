# -*- coding: utf-8 -*-

from tournai.urban.dataimport.architects.mappers import ArchitectFactory
from tournai.urban.dataimport.architects.mappers import IdMapper
from tournai.urban.dataimport.architects.mappers import PhoneMapper

from imio.urban.dataimport.mapper import SimpleMapper


OBJECTS_NESTING = [
    ('ARCHITECT', [],),
]

FIELDS_MAPPINGS = {
    'ARCHITECT':
    {
        'factory': [ArchitectFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'Nom',
                    'to': 'name1',
                },
                {
                    'from': 'Prénom',
                    'to': 'name2',
                },
                {
                    'from': 'Société',
                    'to': 'society',
                },
                {
                    'from': 'Rue',
                    'to': 'street',
                },
                {
                    'from': 'Numéro',
                    'to': 'number',
                },
                {
                    'from': 'CP',
                    'to': 'zipcode',
                },
                {
                    'from': 'Localité',
                    'to': 'city',
                },
                {
                    'from': 'Mail',
                    'to': 'email',
                },
            ),

            IdMapper: {
                'from': ('Nom', 'Société'),
                'to': 'id',
            },

            PhoneMapper: {
                'from': ('Téléphone', 'Gsm'),
                'to': 'phone',
            },
        },
    },
}
