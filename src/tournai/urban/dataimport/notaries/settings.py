# -*- coding: utf-8 -*-

from tournai.urban.dataimport.notaries.importer import NotariesImporter
from imio.urban.dataimport.csv.settings import CSVImporterFromImportSettings


class NotariesImporterFromImportSettings(CSVImporterFromImportSettings):
    """ """

    def __init__(self, settings_form, importer_class=NotariesImporter):
        """
        """
        super(NotariesImporterFromImportSettings, self).__init__(settings_form, importer_class)

    def get_importer_settings(self):
        """
        Return the mdb file to read.
        """
        settings = super(NotariesImporterFromImportSettings, self).get_importer_settings()

        csv_settings = {
            'csv_filename': 'Notaires',
            'key_column': 'NOM',
        }

        settings.update(csv_settings)

        return settings
