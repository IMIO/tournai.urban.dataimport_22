# -*- coding: utf-8 -*-

import csv
import os

import unicodedata
from plone.i18n.normalizer import idnormalizer
from plone import api
from Products.CMFPlone.utils import normalizeString

from imio.urban.dataimport.config import IMPORT_FOLDER_PATH
from imio.urban.dataimport.errors import NoPortalTypeError, IdentifierError
from imio.urban.dataimport.utils import identify_parcel_abbreviations, parse_cadastral_reference, CadastralReference, \
    guess_cadastral_reference
from tournai.urban.dataimport.csv import valuesmapping

cpt_nl = 0
cptFound_nl = 0
cptNotFound_nl = 0

def get_state_from_licences_dates(date_licence, date_refused, date_licence_recourse, date_refused_recourse):

    if date_refused_recourse:
        return 'refuse'
    elif date_licence_recourse:
        return 'accept'
    elif date_refused:
        return 'refuse'
    elif date_licence:
        return 'accept'



def get_date_from_licences_dates(date_licence, date_refused, date_licence_recourse, date_refused_recourse):

    if date_refused_recourse:
        return date_refused_recourse
    elif date_licence_recourse:
        return date_licence_recourse
    elif date_refused:
        return date_refused
    elif date_licence:
        return date_licence


def load_architects():

    csv_filename = 'blc_architects.csv'
    csv_filepath = '{}/{}'.format(IMPORT_FOLDER_PATH, csv_filename)
    csv_file = open(csv_filepath)
    lines = csv.reader(csv_file)

    header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(lines.next())])
    cpt = 1
    for architect in lines:
        print "PROCESSING ARCHITECT %i" % cpt
        cpt += 1
        id_architect = idnormalizer.normalize(('architect_%s%s' % (architect[header_indexes['Nom']], architect[header_indexes['Prenom']])).replace(" ", ""))
        containerArchitects = api.content.get(path='/urban/architects')

        if id_architect not in containerArchitects.objectIds():

            if not (id_architect in containerArchitects.objectIds()):
                object_id = containerArchitects.invokeFactory('Architect', id=id_architect,
                                                    name1=architect[header_indexes['Nom']],
                                                    name2=architect[header_indexes['Prenom']],
                                                    phone=architect[header_indexes['Telephone']],
                                                    gsm=architect[header_indexes['Gsm']],
                                                    email=architect[header_indexes['Email']],
                                                    street=architect[header_indexes['Rue et Numero']],
                                                    zipcode=architect[header_indexes['Code postal']],
                                                    city=architect[header_indexes['Localite']])


def load_geometers():

    csv_filename = 'blc_geometres.csv'
    csv_filepath = '{}/{}'.format(IMPORT_FOLDER_PATH, csv_filename)
    csv_file = open(csv_filepath)
    lines = csv.reader(csv_file)

    header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(lines.next())])
    cpt = 1
    for geometer in lines:
        print "PROCESSING GEOMETER %i" % cpt
        cpt += 1
        id_geometer = idnormalizer.normalize(('geometer_%s%s' % (geometer[header_indexes['Nom']], geometer[header_indexes['Prenom']])).replace(" ", ""))
        containerGeometers = api.content.get(path='/urban/geometricians')

        if id_geometer not in containerGeometers.objectIds():

            if not (id_geometer in containerGeometers.objectIds()):
                object_id = containerGeometers.invokeFactory('Geometrician', id=id_geometer,
                                                    name1=geometer[header_indexes['Nom']],
                                                    name2=geometer[header_indexes['Prenom']],
                                                    phone=geometer[header_indexes['Telephone']],
                                                    gsm=geometer[header_indexes['Gsm']],
                                                    email=geometer[header_indexes['Email']],
                                                    street=geometer[header_indexes['Rue et Numero']],
                                                    zipcode=geometer[header_indexes['Code postal']],
                                                    city=geometer[header_indexes['Localite']])


def load_notaries():

    csv_filename = 'blc_notaires.csv'
    csv_filepath = '{}/{}'.format(IMPORT_FOLDER_PATH, csv_filename)
    csv_file = open(csv_filepath)
    lines = csv.reader(csv_file)

    header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(lines.next())])
    cpt = 1
    for notary in lines:
        print "PROCESSING NOTARY %i" % cpt
        cpt += 1
        id_notary = idnormalizer.normalize(('notary_%s%s' % (notary[header_indexes['Nom']], notary[header_indexes['Prenom']])).replace(" ", ""))
        containerNotaries = api.content.get(path='/urban/notaries')

        if id_notary not in containerNotaries.objectIds():

            if not (id_notary in containerNotaries.objectIds()):
                object_id = containerNotaries.invokeFactory('Notary', id=id_notary,
                                                    name1=notary[header_indexes['Nom']],
                                                    name2=notary[header_indexes['Prenom']],
                                                    phone=notary[header_indexes['Telephone']],
                                                    street='%s %s' % (notary[header_indexes['Adresse1']], notary[header_indexes['Adresse2']]),
                                                    zipcode=notary[header_indexes['Code_postal']],
                                                    city=notary[header_indexes['Ville']])


def create_notary_letters():

    global cpt_nl
    global cptFound_nl
    global cptNotFound_nl

    # delete notary letters parcels stats
    with open("nl_parcel_file_found.csv", "w"):
        pass

    containerNotaryLetters = api.content.get(path='/urban/notaryletters')
    catalog = api.portal.get_tool('portal_catalog')
    for (dirpath, dirnames, filenames) in os.walk(IMPORT_FOLDER_PATH + '/documents'):
        # print(root, dirs, files)
        for notaryletter_file in filenames:
            if '_' in notaryletter_file or '~' in notaryletter_file:
                continue
            cpt_nl += 1
            print "PROCESSING NOTARY LETTER %i" % cpt_nl

            if cpt_nl > 50:
                break
            file_suffix = notaryletter_file.replace(".doc", "").replace(".docx", "").replace(".DOC", "")
            id_notary_letter = idnormalizer.normalize('notary_letter%s' + file_suffix)

            if not (id_notary_letter in containerNotaryLetters.objectIds()):
                object_id = containerNotaryLetters.invokeFactory('NotaryLetter', id=id_notary_letter,
                                                    title="ARCHIVE NOT " + file_suffix,
                                                    reference="ARCHIVE NOT " + file_suffix)
                nl = catalog(portal_type='NotaryLetter', id=id_notary_letter)

                if nl:
                    nl_object = nl[0].getObject()
                    api.content.transition(nl_object, 'accept')

                if object_id:
                    current_letter = api.content.get(path='/urban/notaryletters/' + id_notary_letter)
                    attachment = read_file(os.path.abspath(os.path.join(dirpath, notaryletter_file)))
                    api.content.create(container=current_letter, type='File', id=idnormalizer.normalize("file"+ file_suffix), title=notaryletter_file, file=attachment)
                    # current_letter.invokeFactory('File', id="file_" + id_notary_letter,
                    #                                 title="ARCHIVE NOT" + file_suffix)

                    found = get_parcels_from_filename(file_suffix, current_letter, object_id)

                    if not found:
                        cptNotFound_nl += 1
                    else:
                        cptFound_nl += 1

                    file_name = notaryletter_file
                    document_path = dirpath
                    while True:
                        file_name = file_name[0:len(file_name) - 4] + "_.doc"
                        try:
                            path = path_insensitive(document_path + "/" + file_name)
                            doc = open(path, 'rb')

                        except:
                            # no more _ sequence found : break the infinite loop
                            break
                        doc_content = doc.read()
                        doc.close()

                        api.content.create(container=current_letter, type='File',
                                           id=idnormalizer.normalize("file" + file_name), title=file_name,
                                           file=doc_content)
    # with open("nl_parcel_file_found.csv", "a") as file:
    #     file.write("Doc trouvés :," + str(cpt_nl) + "\n")
    #     file.write("Doc avec parcelle trouvée :," + str(cptFound_nl) + "\n")
    #     file.write("Doc avec parcelle non trouvée :," + str(cptNotFound_nl) + "\n")
    #     if not cptNotFound_nl:
    #         file.write("Pourcentage de réussite :," + str(100) + "%\n")
    #     elif cptFound_nl and cpt_nl:
    #         percentFound = cptFound_nl / cpt_nl * 100
    #         file.write("Pourcentage de réussite :," + str(percentFound) + "%\n")


def read_file(complete_path):

    path = path_insensitive(complete_path)
    doc = open(path, 'rb')
    doc_content = doc.read()
    doc.close()
    return doc_content


def update_description(object_id, message):

    catalog = api.portal.get_tool('portal_catalog')
    nl = catalog(portal_type='NotaryLetter', id=object_id)

    if nl:
        nl_object = nl[0].getObject()
        if str(nl_object.description):
            nl_object.setDescription(str(nl_object.description) + "<p>" + message + "</p>")
        else:
            nl_object.setDescription(message)


def split_text(s):
    from itertools import groupby
    for k,g in groupby(s, str.isalpha):
        yield ''.join(list(g))


def get_parcels_from_filename(file_name, container, object_id):

    file_name = file_name.replace(" ", "")
    if file_name:
        split_name = list(split_text(file_name))
        division = split_name[0]
        division_map = valuesmapping.VALUES_MAPS.get('division_map')
        if '0' == division[0] and len(division) > 1:
            division = division[1]
        division_code = division_map.get(division)
        if not division_code:
            section = ''
            num = ''
            update_description(object_id, "Parcelle : division non trouvée : " + file_name)
            with open("notaryLettersMatchParcelsError.csv", "a") as file:
                file.write(file_name + ", division(%s) section(%s) num(%s)" %(division, section, num) + "\n")
            return False
        if len(split_name) > 1:
            section = split_name[1].upper()
        num = ''
        if len(split_name) >= 2:
            for x in split_name[2:]:
                num += x
            print(division_code, section, num)
            if not division_code or not section or not division or not num:
                update_description(object_id, "Parcelle non trouvée : " + file_name)
                with open("notaryLettersMatchParcelsError.csv", "a") as file:
                    file.write(file_name + ", division(%s) section(%s) num(%s)" %(division, section, num) + "\n")
                return False
            abbreviations = identify_parcel_abbreviations(num)
            if not abbreviations:
                update_description(object_id, "Parcelle non trouvée : " + file_name)
                with open("notaryLettersMatchParcelsError.csv", "a") as file:
                    file.write(file_name + ", division(%s) section(%s) num(%s)" %(division, section, num) + "\n")
                return False
            base_reference = parse_cadastral_reference(division_code + section + abbreviations[0])
            base_reference = CadastralReference(*base_reference)
            if not base_reference:
                update_description(object_id, "Parcelle non trouvée : " + file_name)
                with open("notaryLettersMatchParcelsError.csv", "a") as file:
                    file.write(file_name + ", division(%s) section(%s) num(%s)" %(division, section, num) + "\n")
                return False
            parcels = [base_reference]
            for abbreviation in abbreviations[1:]:
                new_parcel = guess_cadastral_reference(base_reference, abbreviation)
                parcels.append(new_parcel)

            for parcel in parcels:
                create_parcel_in_notary_letter(parcel, container)
            return True
        else:
            return False
    else:
        return False


def create_parcel_in_notary_letter(parcel, container):

    site = api.portal.getSite()
    searchview = site.restrictedTraverse('searchparcels')
    # need to trick the search browser view about the args in its request
    parcel_args = parcel.to_dict()
    parcel_args.pop('partie')

    for k, v in parcel_args.iteritems():
        searchview.context.REQUEST[k] = v
    # check if we can find a parcel in the db cadastre with these infos
    found = searchview.search_parcels_custom(**parcel_args)
    if not found:
        found = searchview.search_parcels_custom(True, **parcel_args)

    if len(found) == 1 and parcel.has_same_attribute_values(found[0].__dict__):
        parcel_args['divisionCode'] = parcel_args['division']
        parcel_args['isOfficialParcel'] = True
    else:
        # self.logError(self, line, 'Too much parcels found or not enough parcels found',
        #               {'args': parcel_args, 'search result': len(found)})
        parcel_args['isOfficialParcel'] = False

    parcel_args['id'] = parcel.id
    parcel_args['partie'] = parcel.partie

    if not (parcel_args['id'] in container.objectIds()):
        object_id = api.content.create(container, type='PortionOut', **parcel_args)
        # with open("notaryletters_new_id.csv", "a") as file:
        #     file.write("new id : %s, %s \n" % (parcel_args['id'] , container))
    else:
        print('%s dans %s' %(parcel_args['id'], container.objectIds()))
        with open("notaryletters_id_already_exists.csv", "a") as file:
            file.write("id already exists : %s, %s \n" % (parcel_args['id'] , container))


def load_parcellings():

    csv_filename = 'blc_lotissements.csv'
    csv_filepath = '{}/{}'.format(IMPORT_FOLDER_PATH, csv_filename)
    csv_file = open(csv_filepath)
    lines = csv.reader(csv_file)

    header_indexes = dict([(headercell.strip(), index) for index, headercell in enumerate(lines.next())])
    cpt = 1
    for parcelling in lines:
        print "PROCESSING PARCELLING %i" % cpt
        cpt += 1
        id_parcelling = idnormalizer.normalize(('parcelling%s%s' % (parcelling[header_indexes['Nom du lotisseur']], parcelling[header_indexes['ReferenceRW']].replace("-", "").replace(".", ""))).replace(" ", ""))
        containerParcellings = api.content.get(path='/urban/parcellings')

        if id_parcelling not in containerParcellings.objectIds():

            if not (id_parcelling in containerParcellings.objectIds()):

                object_id = containerParcellings.invokeFactory('ParcellingTerm', id=id_parcelling,
                                                    title='%s %s' % (parcelling[header_indexes['ReferenceRW']], parcelling[header_indexes['Nom du lotisseur']]),
                                                    label=parcelling[header_indexes['Libelle']],
                                                    subdividerName=parcelling[header_indexes['Nom du lotisseur']],
                                                    authorizationDate=parcelling[header_indexes['Date autorisation']],
                                                    DGO4Reference=parcelling[header_indexes['ReferenceRW']],
                                                    numberOfParcels=parcelling[header_indexes['Nombre de lots']])

                parcel = create_parcel(object_id,
                                       parcelling[header_indexes['Parcelle1Section']],
                                       parcelling[header_indexes['Parcelle1Numero']],
                                       parcelling[header_indexes['Parcelle1NumeroSuite']],
                                       parcelling[header_indexes['AdresseLocalite']])





def create_parcel(parcelling, section1, num1, num1suite, division):

    division_label = division
    if len(section1) > 0:
        section1 = section1[0].upper()
    remaining_reference = '%s %s' % (num1, num1suite)
    if not remaining_reference:
        return []
    abbreviations = identify_parcel_abbreviations(remaining_reference)
    division = '2' if division == u'Wauthier-Braine' else '1'
    if not remaining_reference or not section1:
        return []
    abbrev = '' if len(abbreviations) == 0  else abbreviations[0]
    base_reference = parse_cadastral_reference(division + section1 + abbrev)

    base_reference = CadastralReference(*base_reference)

    parcels = [base_reference]
    for abbreviation in abbreviations[1:]:
        new_parcel = guess_cadastral_reference(base_reference, abbreviation)
        parcels.append(new_parcel)

    # section2 = self.getData('Parcelle2section', line).upper()
    # if section2:
    #     section2 = section2[0]
    #     remaining_reference2 = '%s %s' % (
    #     self.getData('Parcelle2numero', line), self.getData('Parcelle2numerosuite', line))
    #     if not remaining_reference2:
    #         return []
    #
    #     abbreviations2 = identify_parcel_abbreviations(remaining_reference2)
    #     if not remaining_reference2 or not section2:
    #         return []
    #     base_reference2 = parse_cadastral_reference(division + section2 + abbreviations2[0])
    #
    #     base_reference2 = CadastralReference(*base_reference2)
    #
    #     for abbreviation2 in abbreviations2[1:]:
    #         new_parcel2 = guess_cadastral_reference(base_reference2, abbreviation2)
    #         parcels.append(new_parcel2)

    for parcel in parcels:
        searchview = api.portal.get().restrictedTraverse('searchparcels')
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
            # api.portal.get().logError(api.portal.get(), None, 'Too much parcels found or not enough parcels found', {'args': parcel_args, 'search result': len(found)})
            parcel_args['isOfficialParcel'] = False

        parcel_args['id'] = parcel.id
        parcel_args['partie'] = parcel.partie
        container = api.content.get(path='/urban/parcellings/' + parcelling)

        object_id = container.invokeFactory('PortionOut',
                                                    title=parcel_args['id'],
                                                    id=parcel_args['id'],
                                                    isOfficialParcel=parcel_args['isOfficialParcel'],
                                                    division=division_label,
                                                    section=parcel_args['section'],
                                                    puissance=parcel_args['puissance'],
                                                    exposant=parcel_args['exposant'],
                                                    radical=parcel_args['radical'],
                                                    bis=parcel_args['bis'],
                                                    divisionCode=parcel_args['division'])

        return object_id


def get_state_from_raw_conclusion(rawConclusion):

    upperConclusion = rawConclusion.upper()

    if 'REFUS' in upperConclusion or 'DEFAVORABLE' in upperConclusion:
        return 'refuse'
    elif 'AUTORISATION' in upperConclusion or 'FAVORABLE' in upperConclusion:
        return 'accept'
    elif 'RETIRE' in upperConclusion or 'ANNULE' in upperConclusion:
        return 'retire'
    else:
        return ''


def get_decision_from_raw_conclusion(rawConclusion):

    upperConclusion = rawConclusion.upper()

    if 'REFUS' in upperConclusion or 'DEFAVORABLE' in upperConclusion:
        return u"defavorable"
    elif 'AUTORISATION' in upperConclusion or 'FAVORABLE' in upperConclusion or 'APPROUVE' in upperConclusion:
        return u"favorable"
    # elif 'RETIRE' in upperConclusion or 'ANNULE' in upperConclusion:
    #     return 'u"Annulé"'

def get_custom_event(rawConclusion, type):

    upperConclusion = rawConclusion.upper()

    if type == 'EnvClassThree':
        if 'IRRECEVABLE' in upperConclusion:
            return "refus-de-la-demande"
    elif type == 'EnvClassTwo':
        if 'AUTORISATION PARTIELLE' in upperConclusion:
            return "decision"
        elif 'AUTORISATION' in upperConclusion:
            return "decision"
        elif 'REFUS' in upperConclusion or 'ANNULE' in upperConclusion or 'RETIRE' in upperConclusion:
            return "decision-pour-refus"

def delete_csv_report_files():

    # delete rubrics error file content
    with open("matchRubricsError.csv", "w"):
        pass

    # delete notary letter parcel unmatched file content
    with open("notaryLettersMatchParcelsError.csv", "w"):
        pass

    # delete document found file content
    with open("documentfound.csv", "w"):
        pass

    # delete document open error
    with open("documenterror.csv", "w"):
        pass

    # delete document not found file content
    with open("documentnotfound.csv", "w"):
        pass

    # delete notary letters already id exists file content
        with open("notaryletters_id_already_exists.csv", "w"):
            pass

    # delete notary letters new id file content
            with open("notaryletters_new_id.csv", "w"):
                pass





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


def safe_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even it is already a unicode string.

    #     >>> from Products.CMFPlone.utils import safe_unicode
    #
    #     >>> safe_unicode('spam')
    #     u'spam'
    #     >>> safe_unicode(u'spam')
    #     u'spam'
    #     >>> safe_unicode(u'spam'.encode('utf-8'))
    #     u'spam'
    #     >>> safe_unicode('\xc6\xb5')
    #     u'\u01b5'
    #     >>> safe_unicode(u'\xc6\xb5'.encode('iso-8859-1'))
    #     u'\u01b5'
    #     >>> safe_unicode('\xc6\xb5', encoding='ascii')
    #     u'\u01b5'
    #     >>> safe_unicode(1)
    #     1
    #     >>> print safe_unicode(None)
    #     None
    # """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except UnicodeDecodeError:
            value = value.decode('utf-8', 'replace')
    return value


def get_point_and_digits(string):

    return ''.join([letter for letter in string if (letter.isdigit() or letter == '.')]).strip()


def convertToAscii(unicodeString, mode):

    if not isinstance(unicodeString, unicode) or mode != 'replace' and mode != 'ignore':
        raise ValueError

    # convert to ascii, unknown characters are set to '?'/replace mode, ''/ignore mode
    return unicodeString.encode('ascii', mode)


def path_insensitive(path):
    """
    Get a case-insensitive path for use on a case sensitive system.

    >>> path_insensitive('/Home')
    '/home'
    >>> path_insensitive('/Home/chris')
    '/home/chris'
    >>> path_insensitive('/HoME/CHris/')
    '/home/chris/'
    >>> path_insensitive('/home/CHRIS')
    '/home/chris'
    >>> path_insensitive('/Home/CHRIS/.gtk-bookmarks')
    '/home/chris/.gtk-bookmarks'
    >>> path_insensitive('/home/chris/.GTK-bookmarks')
    '/home/chris/.gtk-bookmarks'
    >>> path_insensitive('/HOME/Chris/.GTK-bookmarks')
    '/home/chris/.gtk-bookmarks'
    >>> path_insensitive("/HOME/Chris/I HOPE this doesn't exist")
    "/HOME/Chris/I HOPE this doesn't exist"
    """

    return _path_insensitive(path) or path


def _path_insensitive(path):
    """
    Recursive part of path_insensitive to do the work.
    """

    if path == '' or os.path.exists(path):
        return path

    base = os.path.basename(path)  # may be a directory or a file
    dirname = os.path.dirname(path)

    suffix = ''
    if not base:  # dir ends with a slash?
        if len(dirname) < len(path):
            suffix = path[:len(path) - len(dirname)]

        base = os.path.basename(dirname)
        dirname = os.path.dirname(dirname)

    if not os.path.exists(dirname):
        dirname = _path_insensitive(dirname)
        if not dirname:
            return

    # at this point, the directory exists but not the file

    try:  # we are expecting dirname to be a directory, but it could be a file
        files = os.listdir(dirname)
    except OSError:
        return

    baselow = base.lower()
    try:
        basefinal = next(fl for fl in files if fl.lower() == baselow)
    except StopIteration:
        return

    if basefinal:
        return os.path.join(dirname, basefinal) + suffix
    else:
        return