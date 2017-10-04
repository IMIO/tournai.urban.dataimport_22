# -*- coding: utf-8 -*-

from zope.interface import implements

from imio.urban.dataimport.csv.importer import ICSVImporter
from tournai.urban.dataimport.interfaces import ITournaiDataImporter


class TournaiDataImporter(ICSVImporter):
    """ """

    implements(ITournaiDataImporter)
