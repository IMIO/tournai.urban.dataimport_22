# -*- coding: utf-8 -*-

from imio.urban.dataimport.mapper import Mapper
from imio.urban.dataimport.factory import BaseFactory

from Products.CMFPlone.utils import normalizeString


# Factory
class ParcellingFactory(BaseFactory):
    def getCreationPlace(self, factory_args):
        return self.site.urban.parcellings

    def getPortalType(self, container, **kwargs):
        return 'ParcellingTerm'


class IdMapper(Mapper):
    def mapId(self, line):
        parcel_id = '{ID}{part_1}{part_2}{part_3}'.format(
            ID=self.getData('ID'),
            part_1=self.getData('CODE_COMMU'),
            part_2=self.getData('REFDIREXT'),
            part_3=self.getData('SOUSCOM'),
        )
        parcel_id = normalizeString(parcel_id)
        return parcel_id


class LabelMapper(Mapper):
    def mapLabel(self, line):
        label = '{part_1} {part_2} {part_3} {part_4} {part_5}'.format(
            part_1=self.getData('CODE_COMMU'),
            part_2=self.getData('REFDIREXT'),
            part_3=self.getData('SOUSCOM'),
            part_4=self.getData('TYPE'),
            part_5=self.getData('RUE'),
        )
        return label


class AuthorizationDateMapper(Mapper):

    def mapAuthorizationdate(self, line):
        date = self.getData('DATE_D')
        if not date:
            return date

        split_date = date.split('/')
        year = split_date[-1]
        if year <= 16:
            split_date[-1] = '20' + year
        else:
            split_date[-1] = '19' + year
        return '/'.join(split_date)


class DescriptionMapper(Mapper):
    def mapChangesdescription(self, line):
        description = ''
        code_creat = self.getData('CODE_CREAT')
        if code_creat != '0':
            description = 'code creat: %s' % code_creat

        code_u = self.getData('CODE_UNIQU')
        if code_u:
            description = ' %s<p>code unique: %s </p>' % (description, code_u)

        type_decision = self.getData('TYPEDATE')
        if type_decision == 'pÚrimÚ':
            type_decision = 'Périmé'
        if type_decision:
            description = ' %s<p>type décision: %s </p>' % (description, type_decision)

        rems = self.getData('REM_CREAT')
        if rems:
            description = ' %s<p>remarques: %s </p>' % (description, rems)

        n_modif = self.getData('N_MODIF')
        if n_modif:
            description = ' %s<p>nombre de modifications: %s </p>' % (description, n_modif)

        date_peremption = self.getData('DATEPEREMP')
        if date_peremption:
            description = ' %s<p>date péremption: %s </p>' % (description, date_peremption)

        type_peremption = self.getData('PEREMPT')
        if type_peremption:
            description = ' %s<p>type de péremption: %s </p>' % (description, type_peremption)

        renon = self.getData('RENON')
        if renon:
            description = ' %s<p>renonciation: %s </p>' % (description, renon)

        type_renon = self.getData('RENON_TYPE')
        if type_renon:
            description = ' %s<p>type de renonciation: %s </p>' % (description, type_renon)

        rems_rw = self.getData('REM_RW')
        if rems_rw:
            description = ' %s<p>remarques RW: %s </p>' % (description, rems_rw)

        return description
