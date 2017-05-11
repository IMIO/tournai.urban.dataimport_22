# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.agorawin.importer import AgorawinDataImporter
from tournai.urban.dataimport.interfaces import ITournaiDataImporter


class TournaiDataImporter(AgorawinDataImporter):
    """ """

    implements(ITournaiDataImporter)
