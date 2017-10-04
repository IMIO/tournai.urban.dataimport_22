# -*- coding: utf-8 -*-

from tournai.urban.dataimport.notaries import mapping
from imio.urban.dataimport.csv.importer import CSVDataImporter
from imio.urban.dataimport.mapping import ObjectsMapping
from imio.urban.dataimport.mapping import ValuesMapping


class NotariesImporter(CSVDataImporter):
    """ """


class NotariesMapping(ObjectsMapping):
    """ """

    def getObjectsNesting(self):
        return mapping.OBJECTS_NESTING

    def getFieldsMapping(self):
        return mapping.FIELDS_MAPPINGS


class NotariesValuesMapping(ValuesMapping):
    """ """

    def getValueMapping(self, mapping_name):
        return
