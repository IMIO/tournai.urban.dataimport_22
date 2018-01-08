# -*- coding: utf-8 -*-

from tournai.urban.dataimport.architects.importer import ArchitectsImporter
from imio.urban.dataimport.csv.settings import CSVImporterFromImportSettings
from tournai.urban.dataimport.csv.utils import create_notary_letters


class ArchitectsImporterFromImportSettings(CSVImporterFromImportSettings):
    """ """

    def __init__(self, settings_form, importer_class=ArchitectsImporter):
        """
        """
        super(CSVImporterFromImportSettings, self).__init__(settings_form, importer_class)

    def get_importer_settings(self):
        """
        Return the csv file to read.
        """
        settings = super(ArchitectsImporterFromImportSettings, self).get_importer_settings()

        csv_settings = {
            'csv_filename': 'NL',
            'key_column': 'id',
        }

        settings.update(csv_settings)
        create_notary_letters()

        return settings
