# -*- coding: utf-8 -*-

from tournai.urban.dataimport.architects.importer import ArchitectsImporter
from imio.urban.dataimport.csv.settings import CSVImporterFromImportSettings
from tournai.urban.dataimport.csv.utils import create_notary_letters
import collective.noindexing

import os
import ConfigParser as configparser

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
        self.custom_profile_import()
        return settings

    def custom_profile_import(self):
        # parse option
        # no indexing for notary letters attachment context
        config = configparser.ConfigParser()
        config.read(os.path.join(os.getcwd(), 'src/imio.urban.dataimport/src/imio/urban/dataimport', 'utils.cfg'))
        self.no_index = config.get("no_index", "active") if config.get("no_index", "active") else 0
        if self.no_index:
            collective.noindexing.patches.apply()
        create_notary_letters()
        if self.no_index:
            collective.noindexing.patches.unapply()