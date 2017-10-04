# -*- coding: utf-8 -*-

from imio.urban.dataimport.csv.importer import CSVDataImporter
from imio.urban.dataimport.csv.interfaces import ICSVImporter
from imio.urban.dataimport.browser.adapter import ImporterFromSettingsForm
from imio.urban.dataimport.browser.import_panel import ImporterSettings

from zope.interface import implements

from imio.urban.dataimport.csv.settings import CSVImporterFromImportSettings


class CSVImporterSettings(ImporterSettings):
    """
    """


class TournaiCsvImporterFromImportSettings(CSVImporterFromImportSettings):
    """ """

    def get_importer_settings(self):
        """
        Return the db name to read.
        """
        settings = super(TournaiCsvImporterFromImportSettings, self).get_importer_settings()
        db_settings = {
            'key_column': 'id',
            'csv_filename': 'tournai_20170317',
        }

        settings.update(db_settings)

        return settings
