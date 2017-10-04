# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapper import Mapper
from imio.urban.dataimport.factory import BaseFactory

from Products.CMFPlone.utils import normalizeString


# Factory
class ArchitectFactory(BaseFactory):
    def getCreationPlace(self, factory_args):
        return self.site.urban.architects

    def getPortalType(self, container, **kwargs):
        return 'Architect'


class IdMapper(Mapper):
    def mapId(self, line):
        name = '%s' % self.getData('Nom')
        if not name:
            name = '%s' % self.getData('Société')
        name = name.replace(' ', '').replace('-', '')
        contact_id = normalizeString(self.site.portal_urban.generateUniqueId(name))
        return contact_id


class PhoneMapper(Mapper):
    def mapPhone(self, line):
        phone = self.getData('Téléphone')
        gsm = self.getData('Gsm')

        if (phone and phone != '-') and (gsm and gsm != '-'):
            phones = '{phone}, {gsm}'.format(
                phone=phone,
                gsm=gsm,
            )
            return phones
        elif phone and phone != '-':
            return phone
        elif gsm and gsm != '-':
            return gsm

        return ''
