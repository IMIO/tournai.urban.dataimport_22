# -*- coding: utf-8 -*-

from imio.urban.dataimport.browser.controlpanel import ImporterControlPanel
from imio.urban.dataimport.browser.import_panel import ImporterSettings
from imio.urban.dataimport.browser.import_panel import ImporterSettingsForm
from imio.urban.dataimport.agorawin.settings import AgorawinImporterFromImportSettings


class TournaiImporterSettingsForm(ImporterSettingsForm):
    """ """

class TournaiImporterSettings(ImporterSettings):
    """ """
    form = TournaiImporterSettingsForm


class TournaiImporterControlPanel(ImporterControlPanel):
    """ """
    import_form = TournaiImporterSettings


class TournaiImporterFromImportSettings(AgorawinImporterFromImportSettings):
    """ """

    def get_importer_settings(self):
        """
        Return the db name to read.
        """
        settings = super(TournaiImporterFromImportSettings, self).get_importer_settings()

        db_settings = {
            'db_name': '',
        }

        settings.update(db_settings)

        return settings
