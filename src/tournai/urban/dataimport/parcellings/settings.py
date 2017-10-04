# -*- coding: utf-8 -*-

from tournai.urban.dataimport.parcellings.importer import ParcellingsImporter
from imio.urban.dataimport.csv.settings import CSVImporterFromImportSettings


class ParcellingsImporterFromImportSettings(CSVImporterFromImportSettings):
    """ """

    def __init__(self, settings_form, importer_class=ParcellingsImporter):
        """
        """
        super(CSVImporterFromImportSettings, self).__init__(settings_form, importer_class)

    def get_importer_settings(self):
        """
        Return the csv file to read.
        """
        settings = super(ParcellingsImporterFromImportSettings, self).get_importer_settings()

        csv_settings = {
            'csv_filename': 'Lotissements.csv',
            'key_column': 'n° permis',
        }

        settings.update(csv_settings)

        return settings
