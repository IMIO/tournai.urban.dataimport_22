# -*- coding: utf-8 -*-
import unicodedata

import datetime

from tournai.urban.dataimport.csv.utils import get_state_from_licences_dates, get_date_from_licences_dates, \
    load_architects, load_geometers, load_notaries, load_parcellings, get_state_from_raw_conclusion, \
    get_decision_from_raw_conclusion, get_custom_event, convertToUnicode, get_point_and_digits, convertToAscii, \
    delete_csv_report_files, path_insensitive, create_notary_letters
from imio.urban.dataimport.config import IMPORT_FOLDER_PATH

from imio.urban.dataimport.exceptions import NoObjectToCreateException

from imio.urban.dataimport.factory import BaseFactory
from imio.urban.dataimport.mapper import Mapper, FinalMapper, PostCreationMapper
from imio.urban.dataimport.utils import CadastralReference
from imio.urban.dataimport.utils import cleanAndSplitWord
from imio.urban.dataimport.utils import guess_cadastral_reference
from imio.urban.dataimport.utils import identify_parcel_abbreviations
from imio.urban.dataimport.utils import parse_cadastral_reference

from DateTime import DateTime
from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.utils import safe_unicode

from plone import api
from plone.i18n.normalizer import idnormalizer

import re

import os

#
# LICENCE
#

# factory


class LicenceFactory(BaseFactory):
    def getCreationPlace(self, factory_args):
        path = '%s/urban/%ss' % (self.site.absolute_url_path(), factory_args['portal_type'].lower())
        return self.site.restrictedTraverse(path)

# mappers


class IdMapper(Mapper):

    def __init__(self, importer, args):
        super(IdMapper, self).__init__(importer, args)
        # load_architects()
        # load_geometers()
        # load_notaries()
        # load_parcellings()
        # create_notary_letters(self)
        delete_csv_report_files()

    def mapId(self, line):
        return normalizeString(self.getData('id'))


class ReferenceMapper(Mapper):
    def mapReference(self, line):
        title = 'ARCHIVE'
        object1 = self.getData('GENRE')
        object2 = self.getData('ANNEE')
        object3 = self.getData('DOSNUM')
        return '%s %s - %s - %s' % (title, object1, object2, object3)


class ReferenceDGATLPMapper(Mapper):
    def mapReferencedgatlp(self, line):
        object1 = self.getData('GENRE')
        object2 = self.getData('DOSNUM')
        return '%s - %s' % (object1, object2)


class PortalTypeMapper(Mapper):
    def mapPortal_type(self, line):
        genre = self.getData('GENRE', line)
        if genre:
            if genre.startswith('PB') or genre.startswith('PU'):
                portal_type = 'BuildLicence'
            elif genre.startswith('CL3') or genre.startswith('SEI'):
                portal_type = 'EnvClassThree'
            elif genre.startswith('CU'):
                portal_type = 'UrbanCertificateOne'
            elif genre.startswith('DIV'):
                portal_type = 'Division'
            elif genre.startswith('DU'):
                portal_type = 'Declaration'
            elif genre.startswith('ECI') or genre.startswith('PE'):
                portal_type = 'EnvClassTwo'
            elif genre.startswith('INF') or genre.startswith('PEU') or \
                genre.startswith('PSE') or genre.startswith('SAR') or \
                genre.startswith('ASS') or genre.startswith('CP') or \
                genre.startswith('DF') or genre.startswith('PIC') or \
                genre.startswith('PI') or genre.startswith('PSE'):
                 portal_type = 'MiscDemand'
            else:
                raise NoObjectToCreateException
        else:
            raise NoObjectToCreateException

        return portal_type


    def mapFoldercategory(self, line):
        foldercategory = 'uat'
        return foldercategory


class WorklocationMapper(Mapper):
    def mapWorklocations(self, line):
        num = self.getData('BIENNUM')
        noisy_words = set(('d', 'du', 'de', 'des', 'le', 'la', 'les', 'à', ',', 'rues', 'terrain', 'terrains', 'garage', 'magasin', 'entrepôt'))
        raw_street = self.getData('BIENADR')
        if raw_street.endswith(')'):
            raw_street = raw_street[:-5]
        street = cleanAndSplitWord(raw_street)
        street_keywords = [word for word in street if word not in noisy_words and len(word) > 1]
        if len(street_keywords) and street_keywords[-1] == 'or':
            street_keywords = street_keywords[:-1]

        locality = self.getData('BIENCOM')
        street_keywords.extend(cleanAndSplitWord(locality))

        brains = self.catalog(portal_type='Street', Title=street_keywords)
        if len(brains) == 1:
            return ({'street': brains[0].UID, 'number': num},)
        if street:
            self.logError(self, line, 'Couldnt find street or found too much streets', {
                'address': '%s, %s, %s ' % (num, raw_street, locality),
                'street': street_keywords,
                'search result': len(brains)
            })
        return {}


class WorkTypeMapper(Mapper):
    def mapWorktype(self, line):
        worktype = self.getData('Code_220+')
        return [worktype]


class InquiryStartDateMapper(Mapper):
    def mapInvestigationstart(self, line):
        date = self.getData('DATENQU1')
        try:
            return datetime.datetime.strptime(date, "%d/%m/%Y")
        except ValueError:
            return None


class InquiryEndDateMapper(Mapper):
    def mapInvestigationend(self, line):
        date = self.getData('DATENQU3')
        try:
            return datetime.datetime.strptime(date, "%d/%m/%Y")
        except ValueError:
            return None

class InvestigationReasonsMapper(Mapper):
    def mapInvestigationreasons(self, line):
        reasons = '<p>%s</p> <p>%s</p>' % (self.getData('ParticularitesEnq1'), self.getData('ParticularitesEnq2'))
        return reasons

class InquiryReclamationNumbersMapper(Mapper):
    def mapInvestigationwritereclamationnumber(self, line):
        reclamation = self.getData('NBRec')
        return reclamation


class InquiryArticlesMapper(PostCreationMapper):
    def mapInvestigationarticles(self, line, plone_object):
        raw_articles = self.getData('Enquete')

        articles = []

        if raw_articles:
            article_regex = '(\d+ ?, ?\d+)°'
            found_articles = re.findall(article_regex, raw_articles)

            if not found_articles:
                self.logError(self, line, 'No investigation article found.', {'articles': raw_articles})

            for art in found_articles:
                article_id = re.sub(' ?, ?', '-', art)
                if not self.article_exists(article_id, licence=plone_object):
                    self.logError(
                        self, line, 'Article %s does not exist in the config',
                        {'article id': article_id, 'articles': raw_articles}
                    )
                else:
                    articles.append(article_id)

        return articles

    def article_exists(self, article_id, licence):
        return article_id in licence.getLicenceConfig().investigationarticles.objectIds()


class AskOpinionsMapper(Mapper):
    def mapSolicitopinionsto(self, line):
        ask_opinions = []
        for i in range(60, 76):
            j = i - 59
            if line[i] == "VRAI":
                solicitOpinionDictionary = self.getValueMapping('solicitOpinionDictionary')
                opinion = solicitOpinionDictionary[str(j)]
                if opinion:
                    ask_opinions.append(opinion)
        return ask_opinions


class ObservationsMapper(Mapper):
    def mapDescription(self, line):
        description = '<p>%s</p> <p>%s</p>' % (self.getData('ParticularitesEnq1'),self.getData('ParticularitesEnq2'))
        return description


class TechnicalConditionsMapper(Mapper):
    def mapLocationtechnicalconditions(self, line):
        obs_decision1 = '<p>%s</p>' % self.getData('memo_Autorisation')
        obs_decision2 = '<p>%s</p>' % self.getData('memo_Autorisation2')
        return '%s%s' % (obs_decision1, obs_decision2)


class ArchitectMapper(PostCreationMapper):
    def mapArchitects(self, line, plone_object):
        archi_name = '%s %s %s' % (self.getData('ARCHNOM'), self.getData('ARCHADR'), self.getData('ARCHCOM'))
        fullname = cleanAndSplitWord(archi_name)
        if not fullname:
            return []
        noisy_words = ['monsieur', 'madame', 'architecte', '&', ',', '.', 'or', 'mr', 'mme', '/']
        name_keywords = [word.lower() for word in fullname if word.lower() not in noisy_words]
        architects = self.catalog(portal_type='Architect', Title=name_keywords)
        # link only existing architects
        # if len(architects) == 0:
        #     Utils.createArchitect(archi_name)
        #     architects = self.catalog(portal_type='Architect', Title=name_keywords)
        if len(architects) == 1:
            return architects[0].getObject()
        self.logError(self, line, 'No architects found or too much architects found',
                      {
                          'raw_name': archi_name,
                          'name': name_keywords,
                          'search_result': len(architects)
                      })
        return []


class FolderManagerMapper(Mapper):
    def mapFoldermanagers(self, line):
        foldermanagers = []
        foldermanagers_raw = self.getData('AGENT')
        if foldermanagers_raw:
            for fm in foldermanagers_raw.split("/"):
                fm = fm.strip()
                fm_mapper = self.getValueMapping('foldermanager_map')
                if fm in fm_mapper:
                    fm_tosearch = self.getValueMapping('foldermanager_map')[fm.upper()]
                    if fm_tosearch:
                        foldermanager = self.catalog(portal_type='FolderManager', Title=fm_tosearch)
                        if len(foldermanager) == 1:
                            foldermanagers.append(foldermanager[0].getObject().UID())
                        elif len(foldermanager) == 0:
                            self.logError(self, line, 'foldermanager not found',
                                          {
                                              'foldermanager': foldermanagers_raw,
                                          })
                else:
                    self.logError(self, line, 'foldermanager not found',
                                  {
                                      'foldermanager': foldermanagers_raw,
                                  })
            if foldermanagers_raw == 'MV':
                self.logError(self, line, 'internship found',
                              {
                                  'raw_name': 'MV',
                                  'name': 'Mathieu stagiaire',
                          })
        return foldermanagers


class RubricsMapper(Mapper):

    def mapRubrics(self, line):
        rubric_list = []
        rubric_raw = self.getData('RUBRIQUES')
        if rubric_raw:
            rubric_raw.replace("//", "/")
            rubrics = rubric_raw.split("/")
            if rubrics:
                for rubric in rubrics:
                    point_and_digits = get_point_and_digits(rubric)
                    if point_and_digits and '.' in point_and_digits:
                        catalog = api.portal.get_tool('portal_catalog')
                        rubric_uids = [brain.UID for brain in catalog(portal_type='EnvironmentRubricTerm', id=point_and_digits)]
                        if not rubric_uids:
                                with open("matchRubricsError.csv", "a") as file:
                                    file.write(point_and_digits + "\n")
                                self.logError(self, line, 'No rubric found',
                                              {
                                                  'rubric': point_and_digits,
                                              })
                        else:
                            rubric_list.append(rubric_uids[0])


        return rubric_list


class DocumentIdMapper(Mapper):
    def mapId(self, line):
        doc_id = self.getData('CADDIV') + self.getData('CADSEC') + self.getData('CADNUM')
        if not doc_id or '?' in doc_id:
            raise NoObjectToCreateException
        # doc_id = document_path.split('\\')[-1]
        doc_id = idnormalizer.normalize(doc_id)
        return doc_id


class DocumentTitleMapper(Mapper):
    def mapTitle(self, line):
        doc_id = self.getData('CADDIV') + self.getData('CADSEC') + self.getData('CADNUM')
        if not doc_id or '?' in doc_id:
            raise NoObjectToCreateException
        # doc_id = document_path.split('\\')[-1]
        doc_id = idnormalizer.normalize(doc_id)
        return doc_id


class DocumentsMapper2(Mapper):
    def map(self, line):
        licence = self.importer.current_containers_stack[-1]
        documents_args = []
        for parcel in licence.objectValues():
            if parcel.portal_type == 'PortionOut':
                if parcel.division and parcel.section and parcel.radical:
                    div = None
                    for code, codeDivision in self.getValueMapping('division_map').items():
                        if codeDivision == parcel.division:
                            div = code
                            if len(div) == 1:
                                div = '0' + div

                    if div:
                        file_name = div + parcel.section + parcel.radical + parcel.exposant + parcel.puissance + ".doc"
                        document_path = div + "/" + file_name
                        document_path = '{base}/documents/{rel_path}'.format(
                            base=IMPORT_FOLDER_PATH,
                            rel_path=document_path
                        )

                        try:
                            path = path_insensitive(document_path)
                            doc = open(path, 'rb')
                            # with open("documentfound.csv", "a") as file:
                            #     file.write(path + "\n")

                        except:
                            # print "COULD NOT FIND DOCUMENT {}".format(file_name)
                            with open("documentnotfound.csv", "a") as file:
                                file.write(path + "\n")
                                continue

                        doc_content = doc.read()
                        doc.close()

                        doc_args = {
                            'portal_type': 'File',
                            'id': normalizeString(safe_unicode(file_name)),
                            'title': safe_unicode(file_name),
                            'file': doc_content,
                        }
                        documents_args.append(doc_args)

                        # if found, continue with 'underscore' sequence
                        while True:
                            file_name = file_name[0:len(file_name)-4] + "_.doc"
                            document_path = document_path[0:len(document_path)-4] + "_.doc"
                            try:
                                path = path_insensitive(document_path)
                                doc = open(path, 'rb')

                            except:
                                   # no more _ sequence found : break the infinite loop
                                    break
                            doc_content = doc.read()
                            doc.close()

                            doc_args = {
                                'portal_type': 'File',
                                'id': normalizeString(safe_unicode(file_name)),
                                'title': safe_unicode(file_name),
                                'file': doc_content,
                            }
                            documents_args.append(doc_args)

        return documents_args


class FolderZoneTableMapper(Mapper):
    def mapFolderzone(self, line):
        folderZone = []
        sectorMap1 = self.getData('Plan de Secteur 1')
        sectorMap2 = self.getData('Plan de Secteur 2')

        zoneDictionnary = self.getValueMapping('zoneDictionary')

        if sectorMap1 in zoneDictionnary:
            folderZone.append(zoneDictionnary[sectorMap1])

        if sectorMap2 in zoneDictionnary:
            folderZone.append(zoneDictionnary[sectorMap2])

        return folderZone


class GeometricianMapper(PostCreationMapper):
    def mapGeometricians(self, line, plone_object):
        title_words = [word for word in self.getData('Titre').lower().split()]
        for word in title_words:
            if word not in ['géometre', 'géomètre']:
                return
        name = self.getData('Nom')
        firstname = self.getData('Prenom')
        raw_name = firstname + name
        name = cleanAndSplitWord(name)
        firstname = cleanAndSplitWord(firstname)
        names = name + firstname
        geometrician = self.catalog(portal_type='Geometrician', Title=names)
        if not geometrician:
            geometrician = self.catalog(portal_type='Geometrician', Title=name)
        if len(geometrician) == 1:
            return geometrician[0].getObject()
        self.logError(self, line, 'no geometricians found or too much geometricians found',
                      {
                          'raw_name': raw_name,
                          'title': self.getData('Titre'),
                          'name': name,
                          'firstname': firstname,
                          'search_result': len(geometrician)
                      })
        return []


class PcaUIDMapper(Mapper):

    def mapPca(self, line):
        title = self.getData('PPA')
        if title:
            catalog = api.portal.get_tool('portal_catalog')
            pca_id = catalog(portal_type='PcaTerm', Title=title)[0].id
            return pca_id
        return []


class IsInPcaMapper(Mapper):

    def mapIsinpca(self, line):
        title = self.getData('PPA')
        return bool(title)


class EnvRubricsMapper(Mapper):

    def mapDescription(self, line):
        rubric = Utils().convertToUnicode(self.getData('LibNat'))
        return rubric


class CompletionStateMapper(PostCreationMapper):
    def map(self, line, plone_object):
        # self.line = line
        # rawConclusion = self.getData('CONCLUSION')
        # transition = get_state_from_raw_conclusion(rawConclusion)
        #
        # if transition:
        #     api.content.transition(plone_object, transition)
        #     # api.content.transition(plone_object, 'nonapplicable')

        api.content.transition(plone_object, 'accept')


class ErrorsMapper(FinalMapper):
    def mapDescription(self, line, plone_object):

        line_number = self.importer.current_line
        errors = self.importer.errors.get(line_number, None)
        description = plone_object.Description()

        error_trace = []
        if errors:
            for error in errors:
                data = error.data
                if 'streets' in error.message:
                    error_trace.append('<p>adresse : %s</p>' % data['address'])
                elif 'notaries' in error.message:
                    error_trace.append('<p>notaire : %s %s %s</p>' % (data['title'], data['firstname'], data['name']))
                elif 'architects' in error.message:
                    error_trace.append('<p>architecte : %s</p>' % data['raw_name'])
                elif 'geometricians' in error.message:
                    error_trace.append('<p>géomètre : %s</p>' % data['raw_name'])
                elif 'parcelling' in error.message:
                    error_trace.append('<p>lotissement : %s %s, autorisé le %s</p>' % (data['approval date'], data['city'], data['auth_date']))
                elif 'article' in error.message.lower():
                    error_trace.append('<p>Articles de l\'enquête : %s</p>' % (data['articles']))
                elif 'foldermanager' in error.message.lower():
                    error_trace.append('<p>Agent : %s</p>' % (data['foldermanager']))
                elif 'rubric' in error.message.lower():
                    error_trace.append('<p>Rubrique non trouvée : %s</p>' % (data['rubric']))
                elif 'internship' in error.message.lower():
                            error_trace.append('<p>Encodé par le stagiaire Mathieu V</p>')
        error_trace = ''.join(error_trace)

        return '%s%s' % (error_trace, description)


#
# CONTACT
#

# factory


class ContactFactory(BaseFactory):
    def getPortalType(self, container, **kwargs):
        if container.portal_type in ['UrbanCertificateOne', 'UrbanCertificateTwo', 'Division']:
            return 'Proprietary'
        return 'Applicant'

# mappers


class ContactIdMapper(Mapper):
    def mapId(self, line):
        name = '%s%s%s' % (self.getData('DEMNOM'), self.getData('DEMPRE'), self.getData('id'))
        name = name.replace(' ', '').replace('-', '')
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class ContactTitleMapper(Mapper):
    def mapPersontitle(self, line):
        title1 = self.getData('Civi').lower()
        title = title1 or self.getData('Civi2').lower()
        title_mapping = self.getValueMapping('titre_map')
        return title_mapping.get(title, 'notitle')


class ContactNameMapper(Mapper):
    def mapName1(self, line):
        title = self.getData('Civi2')
        name = self.getData('D_Nom')
        regular_titles = [
            'M.',
            'M et Mlle',
            'M et Mme',
            'M. et Mme',
            'M. l\'Architecte',
            'M. le président',
            'Madame',
            'Madame Vve',
            'Mademoiselle',
            'Maître',
            'Mlle et Monsieur',
            'Mesdames',
            'Mesdemoiselles',
            'Messieurs',
            'Mlle',
            'MM',
            'Mme',
            'Mme et M',
            'Monsieur',
            'Monsieur,',
            'Monsieur et Madame',
            'Monsieur l\'Architecte',
        ]
        if title not in regular_titles:
            name = '%s %s' % (title, name)
        return name


class ContactSreetMapper(Mapper):
    def mapStreet(self, line):
        regex = '((?:[^\d,]+\s*)+),?'
        raw_street = self.getData('D_Adres')
        match = re.match(regex, raw_street)
        if match:
            street = match.group(1)
        else:
            street = raw_street
        return street


class ContactNumberMapper(Mapper):
    def mapNumber(self, line):
        regex = '(?:[^\d,]+\s*)+,?\s*(.*)'
        raw_street = self.getData('D_Adres')
        number = ''

        match = re.match(regex, raw_street)
        if match:
            number = match.group(1)
        return number


class ContactPhoneMapper(Mapper):
    def mapPhone(self, line):
        raw_phone = self.getData('D_Tel')
        gsm = self.getData('D_GSM')
        phone = ''
        if raw_phone:
            phone = raw_phone
        if gsm:
            phone = phone and '%s %s' % (phone, gsm) or gsm
        return phone



#
# PARCEL
#

#factory


class ParcelFactory(BaseFactory):
    def create(self, parcel, container=None, line=None):
        searchview = self.site.restrictedTraverse('searchparcels')
        #need to trick the search browser view about the args in its request
        parcel_args = parcel.to_dict()
        parcel_args.pop('partie')

        for k, v in parcel_args.iteritems():
            searchview.context.REQUEST[k] = v
        #check if we can find a parcel in the db cadastre with these infos

        found = searchview.search_parcels_custom(**parcel_args)
        if not found:
            found = searchview.search_parcels_custom(True, **parcel_args)

        if len(found) == 1 and parcel.has_same_attribute_values(found[0].__dict__):
            parcel_args['divisionCode'] = parcel_args['division']
            parcel_args['isOfficialParcel'] = True
        else:
            self.logError(self, line, 'Too much parcels found or not enough parcels found', {'args': parcel_args, 'search result': len(found)})
            parcel_args['isOfficialParcel'] = False

        parcel_args['id'] = parcel.id
        parcel_args['partie'] = parcel.partie

        return super(ParcelFactory, self).create(parcel_args, container=container)

    def objectAlreadyExists(self, parcel, container):
        existing_object = getattr(container, parcel.id, None)
        return existing_object

# mappers


class ParcelDataMapper(Mapper):
    def map(self, line, **kwargs):
        division = None
        section = self.getData('CADSEC', line).upper()
        remaining_reference = self.getData('CADNUM', line)
        if not remaining_reference:
            return []
        abbreviations = identify_parcel_abbreviations(remaining_reference)
        if self.getData('CADDIV', line):
            division_map = self.getValueMapping('division_map')
            division = division_map.get(self.getData('CADDIV', line))

        if not remaining_reference or not section or not division:
            return []
        base_reference = parse_cadastral_reference(division + section + abbreviations[0])

        base_reference = CadastralReference(*base_reference)

        parcels = [base_reference]
        for abbreviation in abbreviations[1:]:
            new_parcel = guess_cadastral_reference(base_reference, abbreviation)
            parcels.append(new_parcel)

        return parcels


#
# UrbanEvent deposit
#

# factory
class UrbanEventFactory(BaseFactory):
    def getPortalType(self, **kwargs):
        return 'UrbanEvent'

    def create(self, kwargs, container, line):
        if not kwargs['eventtype']:
            return []
        eventtype_uid = kwargs.pop('eventtype')
        urban_event = container.createUrbanEvent(eventtype_uid, **kwargs)
        return urban_event

#mappers


class DepositEventMapper(Mapper):

    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'depot-de-la-demande'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DepositDate_1_Mapper(Mapper):

    def mapEventdate(self, line):
        date = self.getData('Recepisse')
        if not date:
            raise NoObjectToCreateException
        date = date and DateTime(date) or None
        return date


class DepositEvent_1_IdMapper(Mapper):

    def mapId(self, line):
        return 'deposit-1'


#
# UrbanEvent ask opinions
#

# factory


class OpinionMakersFactory(BaseFactory):
    """ """

#mappers


class OpinionMakersTableMapper(Mapper):
    """ """
    def map(self, line, **kwargs):
        lines = self.query_secondary_table(line)
        for secondary_line in lines:
            for mapper in self.mappers:
                return mapper.map(secondary_line, **kwargs)
            break
        return []


class OpinionMakersMapper(Mapper):

    def map(self, line):
        opinionmakers_args = []
        for i in range(1, 11):
            opinionmakers_id = self.getData('Org{}'.format(i), line)
            if not opinionmakers_id:
                return opinionmakers_args
            event_date = self.getData('Cont{}'.format(i), line)
            receipt_date = self.getData('Rec{}'.format(i), line)
            args = {
                'id': opinionmakers_id,
                'eventtype': opinionmakers_id,
                'eventDate': event_date and DateTime(event_date) or None,
                'transmitDate': event_date and DateTime(event_date) or None,
                'receiptDate': receipt_date and DateTime(receipt_date) or None,
                'receivedDocumentReference': self.getData('Ref{}'.format(i), line),
            }
            opinionmakers_args.append(args)
        if not opinionmakers_args:
            raise NoObjectToCreateException
        return opinionmakers_args


class LinkedInquiryMapper(PostCreationMapper):

    def map(self, line, plone_object):
        opinion_event = plone_object
        licence = opinion_event.aq_inner.aq_parent
        inquiry = licence.getInquiries() and licence.getInquiries()[-1] or licence
        opinion_event.setLinkedInquiry(inquiry)


#
# Claimant
#

# factory


class ClaimantFactory(BaseFactory):
    def getPortalType(self, container, **kwargs):
        return 'Claimant'

#mappers

class ClaimantIdMapper(Mapper):
    def mapId(self, line):
        name = '%s%s' % (self.getData('RECNom'), self.getData('RECPrenom'))
        name = name.replace(' ', '').replace('-', '')
        if not name:
            raise NoObjectToCreateException
        return normalizeString(self.site.portal_urban.generateUniqueId(name))


class ClaimantTitleMapper(Mapper):
    def mapPersontitle(self, line):
        title = self.getData('Civi_Rec').lower()
        title_mapping = self.getValueMapping('titre_map')
        return title_mapping.get(title, 'notitle')


class ClaimantSreetMapper(Mapper):
    def mapStreet(self, line):
        regex = '((?:[^\d,]+\s*)+),?'
        raw_street = self.getData('RECAdres')
        match = re.match(regex, raw_street)
        if match:
            street = match.group(1)
        else:
            street = raw_street
        return street


class ClaimantNumberMapper(Mapper):
    def mapNumber(self, line):
        regex = '(?:[^\d,]+\s*)+,?\s*(.*)'
        raw_street = self.getData('RECAdres')
        number = ''

        match = re.match(regex, raw_street)
        if match:
            number = match.group(1)
        return number

#
# UrbanEvent second RW
#

#mappers


class SecondRWEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = 'transmis-2eme-dossier-rw'
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class SecondRWEventDateMapper(Mapper):
    def mapEventdate(self, line):
        date = self.getData('UR_Datenv2')
        date = date and DateTime(date) or None
        if not date:
            raise NoObjectToCreateException
        return date


class SecondRWDecisionMapper(Mapper):
    def mapExternaldecision(self, line):
        raw_decision = self.getData('UR_Avis')
        decision = self.getValueMapping('externaldecisions_map').get(raw_decision, [])
        return decision


class SecondRWDecisionDateMapper(Mapper):
    def mapDecisiondate(self, line):
        date = self.getData('UR_Datpre')
        date = date and DateTime(date) or None
        return date


class SecondRWReceiptDateMapper(Mapper):
    def mapReceiptdate(self, line):
        date = self.getData('UR_Datret')
        date = date and DateTime(date) or None
        return date

#
# UrbanEvent decision
#

#mappers


class DecisionEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['decision_event']
        if eventtype_id == 'custom':
            eventtype_id = get_custom_event(self.getData('CONCLUSION'), licence.portal_type)
            if not eventtype_id:
                raise NoObjectToCreateException

        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DecisionEventIdMapper(Mapper):
    def mapId(self, line):
        return 'decision-event'


class DecisionDateMapper(Mapper):
    def mapDecisiondate(self, line):
        dateDecision = self.getData('CEPU')
        if not dateDecision:
            raise NoObjectToCreateException
        try:
            datetime.datetime.strptime(dateDecision, "%d/%m/%Y")
            return dateDecision
        except ValueError:
            raise NoObjectToCreateException


class DecisionEventDecisionMapper(Mapper):
    def mapDecision(self, line):
        rawConclusion = self.getData('CONCLUSION')
        decision = get_decision_from_raw_conclusion(rawConclusion)
        if decision:
            return decision
        else:
            raise NoObjectToCreateException


class DecisionTextMapper(Mapper):
    def mapDecisiontext(self, line):
        details = self.getData('CONCLUSION')
        if details:
            textarea_details = u"<span>" + convertToUnicode(details) + u"</span>"
            return textarea_details


class DecisionEventDateMapper(Mapper):
    def mapEventdate(self, line):
        dateDecisionNotif = self.getData('CEPU')
        try:
            datetime.datetime.strptime(dateDecisionNotif, "%d/%m/%Y")
            return dateDecisionNotif
        except ValueError:
            raise NoObjectToCreateException


class DepositEventTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['deposit_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class DepositDateMapper(Mapper):
    def mapEventdate(self, line):
        dateDeposit = self.getData('DATEDEPO')
        try:
            datetime.datetime.strptime(dateDeposit, "%d/%m/%Y")
            return dateDeposit
        except ValueError:
            raise NoObjectToCreateException


class DepositEventIdMapper(Mapper):
    def mapId(self, line):
        licence = self.importer.current_containers_stack[-1]
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['deposit_event']
        return eventtype_id



class CollegeReportTypeMapper(Mapper):
    def mapEventtype(self, line):
        licence = self.importer.current_containers_stack[-1]
        urban_tool = api.portal.get_tool('portal_urban')
        eventtype_id = self.getValueMapping('eventtype_id_map')[licence.portal_type]['college_report_event']
        config = urban_tool.getUrbanConfig(licence)
        return getattr(config.urbaneventtypes, eventtype_id).UID()


class CollegeReportIdMapper(Mapper):
    def mapId(self, line):
        return 'college_report_event'


class CollegeReportEventDateMapper(Mapper):
    def mapEventdate(self, line):
        eventDate = self.getData('Rapport du College')
        if eventDate:
            return eventDate
        else:
            raise NoObjectToCreateException



#
# UrbanEvent suspension
#


# factory
class SuspensionEventFactory(UrbanEventFactory):

    def create(self, kwargs, container, line):
        if not kwargs['eventtype']:
            return []
        eventtype_uid = kwargs.pop('eventtype')
        suspension_reason = kwargs.pop('suspensionReason')
        urban_event = container.createUrbanEvent(eventtype_uid, **kwargs)
        urban_event.setSuspensionReason(suspension_reason)
        return urban_event
#
# Documents
#

# factory


class DocumentsFactory(BaseFactory):
    """ """
    def getPortalType(self, container, **kwargs):
        return 'File'


# *** Utils ***

class Utils():
    @staticmethod
    def convertToUnicode(string):

        if isinstance(string, unicode):
            return string

        # convert to unicode if necessary, against iso-8859-1 : iso-8859-15 add € and oe characters
        data = ""
        if string and isinstance(string, str):
            try:
                data = unicodedata.normalize('NFKC', unicode(string, "iso-8859-15"))
            except UnicodeDecodeError:
                import ipdb; ipdb.set_trace() # TODO REMOVE BREAKPOINT
        return data

    @staticmethod
    def createArchitect(name):

        idArchitect = idnormalizer.normalize(name + 'Architect').replace(" ", "")
        containerArchitects = api.content.get(path='/urban/architects')

        if idArchitect not in containerArchitects.objectIds():
            new_id = idArchitect
            new_name1 = name

            if not (new_id in containerArchitects.objectIds()):
                    object_id = containerArchitects.invokeFactory('Architect', id=new_id,
                                                        name1=new_name1)