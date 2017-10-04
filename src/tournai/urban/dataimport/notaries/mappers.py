# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapper import Mapper
from imio.urban.dataimport.factory import BaseFactory

from Products.CMFPlone.utils import normalizeString

import re


# Factory
class NotaryFactory(BaseFactory):
    def getCreationPlace(self, factory_args):
        return self.site.urban.notaries

    def getPortalType(self, container, **kwargs):
        return 'Notary'


class IdMapper(Mapper):
    def mapId(self, line):
        name = '%s' % self.getData('NOM')
        name = name.replace(' ', '').replace('-', '')
        contact_id = normalizeString(self.site.portal_urban.generateUniqueId(name))
        return contact_id


class AddressMapper(Mapper):

    regex = '(\D*?)(?:(?:,?\s*)|(?:n°\s*))(\d.*)'

    def mapStreet(self, line):
        address = self.getData('ADRESSE')
        street = re.search(self.regex, address)
        if street:
            return street.group(1)
        return ''

    def mapNumber(self, line):
        address = self.getData('ADRESSE')
        number = re.search(self.regex, address)
        if number:
            return number.group(2)
        return ''


class TitleMapper(Mapper):

    def mapPersontitle(self, line):
        title = self.getData('TITRE')
        if title:
            return 'master'
        return 'masters'
