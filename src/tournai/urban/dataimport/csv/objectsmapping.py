# -*- coding: utf-8 -*-

from tournai.urban.dataimport.csv.mappers import *
from imio.urban.dataimport.mapper import SimpleMapper

OBJECTS_NESTING = [
    (
        'LICENCE', [
            ('CONTACT', []),
            # ('PARCEL', []),
            ('DEPOSIT EVENT', []),
            ('DECISION EVENT', []),
            # ('DOCUMENTS', []),
        ],
    ),
]

FIELDS_MAPPINGS = {
    'LICENCE':
    {
        'factory': [LicenceFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'DOSLIB',
                    'to': 'licenceSubject',
                },
                {
                    'from': 'DELAI',
                    'to': 'annoncedDelay',
                },
            ),

            ReferenceDGATLPMapper: {
                'from': ('GENRE', 'DOSNUM'),
                'to': 'referenceDGATLP',
            },

            ReferenceMapper: {
                'from': ('DOSNUM', 'ANNEE', 'GENRE'),
                'to': 'reference',
            },

            IdMapper: {
                'from': 'id',
                'to': 'id',
            },

            PortalTypeMapper: {
                'from': 'GENRE',
                'to': ('portal_type', 'folderCategory',)
            },

            WorklocationMapper: {
                'from': ('BIENADR', 'BIENNUM', 'BIENCOD', 'BIENCOM'),
                'to': 'workLocations',
            },

           ArchitectMapper: {
               'allowed_containers': ['BuildLicence'],
               'from': ('ARCHNOM', 'ARCHADR', 'ARCHCOM'),
               'to': ('architects',)
           },

           FolderManagerMapper: {
               'from': 'AGENT',
               'to': 'foldermanagers',
           },


           #  FolderZoneTableMapper: {
           #     'from': ('ZONEPS'),
           #     'to': 'folderZone',
           # },
            InquiryStartDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': 'DATENQU1',
                'to': 'investigationStart',
            },
            InquiryEndDateMapper: {
                'allowed_containers': ['BuildLicence', 'ParcelOutLicence', 'UrbanCertificateTwo'],
                'from': 'DATENQU3',
                'to': 'investigationEnd',
            },

            RubricsMapper: {
                'from': 'RUBRIQUES',
                'to': 'rubrics'
            },

#            GeometricianMapper: {
#                'allowed_containers': ['ParcelOutLicence'],
#                'from': ('Titre', 'Nom', 'Prenom'),
#                'to': ('geometricians',)
#            },

            # ParcellingsMapper: {
            #     'table': 'LOTISSEM',
            #     'KEYS': ('Cle_Urba', 'Cle_Lot'),
            #     'mappers': {
            #         SimpleMapper: (
            #             {
            #                 'from': 'Lot',
            #                 'to': 'subdivisionDetails',
            #             },
            #         ),
            #         ParcellingUIDMapper: {
            #             'from': 'Lotis',
            #             'to': 'parcellings',
            #         },
            #
            #         IsInSubdivisionMapper: {
            #             'from': 'Lotis',
            #             'to': 'isInSubdivision',
            #         }
            #     },
            # },
            #
            # PcaMapper: {
            #     'table': 'PPA',
            #     'KEYS': ('Cle_Urba', 'Cle_PPA'),
            #     'mappers': {
            #         SimpleMapper: (
            #             {
            #                 'from': 'PPA_Affectation',
            #                 'to': 'pcaDetails',
            #             },
            #         ),
            #         PcaUIDMapper: {
            #             'from': 'PPA',
            #             'to': 'pca',
            #         },
            #
            #         IsInPcaMapper: {
            #             'from': 'PPA',
            #             'to': 'isInPCA',
            #         }
            #     },
            # },

            # EnvRubricsMapper: {
            #     'allowed_containers': ['EnvClassOne', 'EnvClassTwo', 'EnvClassThree'],
            #     'from': 'LibNat',
            #     'to': 'description',
            # },
            #
            CompletionStateMapper: {
                'from': 'CONCLUSION',
                'to': (),  # <- no field to fill, its the workflow state that has to be changed
            },

            ErrorsMapper: {
                'from': (),
                'to': ('description',),  # log all the errors in the description field
            }
        },
    },

    'PARCEL':
    {
        'factory': [ParcelFactory, {'portal_type': 'PortionOut'}],

        'mappers': {
            ParcelDataMapper: {
                'from': ('CADDIV', 'CADSEC', 'CADNUM'),
                'to': (),
            },
        },
    },

    'CONTACT':
    {
        'factory': [ContactFactory],

        'mappers': {
            SimpleMapper: (
                {
                    'from': 'DEMNOM',
                    'to': 'name1',
                },
                {
                    'from': 'DEMPRE',
                    'to': 'name2',
                },
                {
                    'from': ('DEMADR'),
                    'to': 'street',
                },
                {
                    'from': ('DEMCOM'),
                    'to': 'locality',
                },
                {
                    'from': 'TITREA',
                    'to': 'personTitle',
                },
            ),

            ContactIdMapper: {
                'from': ('DEMNOM', 'DEMPRE', 'id'),
                'to': 'id',
            },
        },
    },

    'DECISION EVENT':
    {
        'factory': [UrbanEventFactory],
        'allowed_containers': ['BuildLicence', 'Declaration', 'Division', 'UrbanCertificateOne', 'MiscDemand'],

        'mappers': {
            DecisionEventTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            DecisionEventIdMapper: {
                'from': (),
                'to': 'id',
            },

            DecisionDateMapper: {
                'from': 'CEPU',
                'to': 'decisionDate',
            },

            DecisionEventDateMapper: {
                'from': 'CEPU',
                'to': 'eventDate',
            },

            DecisionEventDecisionMapper: {
                'from': 'CONCLUSION',
                'to': 'decision',
            },

            DecisionTextMapper: {
                'from': 'CONCLUSION',
                'to': 'decisionText',
            }
        },
    },

    'DEPOSIT EVENT':
        {
            'factory': [UrbanEventFactory],

            'mappers': {
                DepositEventTypeMapper: {
                    'from': (),
                    'to': 'eventtype',
                },

                DepositEventIdMapper: {
                    'from': (),
                    'to': 'id',
                },

                DepositDateMapper: {
                    'from': 'DATEDEPO',
                    'to': 'eventDate',
                },


            },
        },

    'COLLEGE REPORT EVENT':
    {
        'factory': [UrbanEventFactory],

        'mappers': {
            CollegeReportTypeMapper: {
                'from': (),
                'to': 'eventtype',
            },

            CollegeReportIdMapper: {
                'from': (),
                'to': 'id',
            },

            CollegeReportEventDateMapper: {
                'from': ('Rapport du College'),
                'to': 'eventDate',
            }
        },
    },

    'DOCUMENTS':
    {
        'factory': [DocumentsFactory],

        'mappers': {
            DocumentsMapper2: {
                    'from': ('CADDIV', 'CADSEC', 'CADNUM'),
                    'to': 'file',
            }
            # DocumentTitleMapper: {
            #     'from': ('CADDIV', 'CADSEC', 'CADNUM'),
            #     'to': 'title',
            # },
            # DocumentIdMapper: {
            #     'from': ('CADDIV', 'CADSEC', 'CADNUM'),
            #     'to': 'id',
            # },
            # DocumentFileMapper: {
            #     'from': ('CADDIV', 'CADSEC', 'CADNUM'),
            #     'to': 'file',
            #         },
        },
    },
}