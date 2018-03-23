# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapping import table

VALUES_MAPS = {

    'eventtype_id_map': table({
        'header'             : ['decision_event', 'college_report_event', 'deposit_event'],
        'BuildLicence'       : ['delivrance-du-permis-octroi-ou-refus', 'rapport-du-college', 'depot-de-la-demande'],
        'Declaration'        : ['deliberation-college', '', 'copy_of_depot-de-la-demande'],
        'Division'        :    ['decision-octroi-refus', '', 'depot-de-la-demande'],
        'UrbanCertificateOne': ['octroi-cu1', '', 'copy_of_depot-de-la-demande'],
        'MiscDemand'         : ['deliberation-college', '', 'depot-de-la-demande'],
        'EnvClassTwo'        : ['custom', '', 'depot-de-la-demande'], #event != octroi/refus
        'EnvClassThree'      : ['custom', '', 'depot-de-la-demande-de-cl3'], #event != octroi/refus/cond
        'PatrimonyCertificate':['decision', '', 'depot-de-la-demande'],
    }),

    'solicitOpinionDictionary': {
               '1' :        "service-technique-provincial", #Avis Service technique provincial
               '2' :        "direction-des-cours-deau", #Avis Dir Cours d'eau
               '3' :        "pi", #Avis Zone de secours
               '4' :        "ores", #Avis ORES
               '5' :        "cibe", #Avis Vivaqua
               '6' :        "agriculture", #Avis Dir Développement rural
               '7' :        "dnf", #Avis Département Nature et Forêts
               '8' :        "forces-armees", #Avis Forces armées
               '9' :        "spw-dgo1", #Avis Dir Routes BW
               '10':        "swde", #Avis SWDE/IECBW
               '11':        "belgacom", #Avis PROXIMUS
               '12':        "infrabel", #Avis TEC
               '13':        "ibw", #Avis IBW
               '14':        "voo", #Avis VOO
               '15':        "bec", #Avis Service technique communal
               '16':        "ccatm", #Avis CCATM
            },

    'zoneDictionary': {
           "zone d'habitat à caractère rural"                                      : 'zhcr'                                         ,
           "zone agricole"                                                         : 'za'                                           ,
           "zone agricole d'intérêt paysager"                                      : 'zone-agricole-dinteret-paysager'              ,
           "zone d'activité économique industrielle"                               : 'zaei'                                         ,
           "zone d'activité économique industrielle (Wauthier-Braine)"             : 'zaei'                                         ,
           "zone d'activité économique mixte"                                      : 'zaem'                                         ,
           "zone d'aménagement communal concerté"                                  : 'zone-damenagement-communal-concerte'          ,
           "zone d'aménagement différé"                                            : 'zone-damenagement-differe'                    ,
           "zone d'espaces verts"                                                  : 'zev'                                          ,
           "zone d'espaces verts d'intérêt paysager"                               : 'zone-despaces-verts-dinteret-paysager'        ,
           "zone d'extraction"                                                     : 'ze'                                           ,
           "zone d'extraction sur fond de zone agricole"                           : 'zone-dextraction-sur-fond-de-zone-agricole'   ,
           "zone d'habitat"                                                        : 'zh'                                           ,
           "zone de loisirs"                                                       : 'zl'                                           ,
           "zone de parc"                                                          : 'zp'                                           ,
           "zone de parc d'intérêt paysager"                                       : 'zone-de-parc-dinteret-paysager'               ,
           "zone de services publics et d'équipements communautaires"              : 'zspec'                                        ,
           "zone forestière"                                                       : 'zf'                                           ,
           "zone forestière d'intérêt paysager"                                    : 'zone-forestiere-dinteret-paysager'            ,
           "zone non affectée"                                                     : 'zone-non-affectee'                            ,
    },

    'event_state_map': {
        'BuildLicence': [u'Octroi du permis'],
        'ParcelOutLicence': [u"octroi du permis d'urbanisation"],
        'Article127': [u'Octroi du permis', u'OctroiPermis' , u'octroi permis'],
        'NotaryLetter': '',
        'UrbanCertificateOne': [u'CU1'],
        'UrbanCertificateTwo': [u'CU2'],
        'Declaration': [u'délivrance permis'],
        'Division': [u'délivrance permis'],
        'MiscDemand': [u'Délivrance autorisation'],
    },

    'division_map': {
        "14": "57005",
        "12": "57007",
        "29": "57008",
        "19": "57021",
        "21": "57022",
        "26": "57024",
        "23": "57030",
        "32": "57031",
        "16": "57033",
        "9": "57036",
        "28": "57038",
        "4": "57042",
        "27": "57044",
        "25": "57050",
        "13": "57052",
        "8": "57053",
        "5": "57056",
        "7": "57057",
        "24": "57060",
        "10": "57068",
        "31": "57069",
        "6": "57073",
        "20": "57076",
        "30": "57078",
        "11": "57080",
        "1": "57081",
        "18": "57082",
        "15": "57084",
        "17": "57085",
        "22": "57092",
        "2": "57462",
        "3": "57463",
    },

    'foldermanager_map': {
        "AD": "Aurore Derumier",
        "NC": "Nabila Charara",
        "CF": "Christine Froidbise",
        "CF ": "Christine Froidbise",
        "JH": "Joel Hache",
        "CDE": "Christophe Delcourt",
        "BL": "Bernadette Larcy",
        "PHM": "Philippe Merlino",
        "DC": "Dominique Cauvin",
        "CD": "Charles Dewart",
        "MM": "Michael Moine",
        "ML": "Monique Luc",
        "MV": "Mathieu stagiaire",
        "LR": "Line Renaux",
        "FH": "Fabienne Herregodts",
        "DV": "Dolores Vanderclausen",
    },
}