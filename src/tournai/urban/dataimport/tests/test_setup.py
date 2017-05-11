# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from tournai.urban.dataimport.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of tournai.urban.dataimport into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if tournai.urban.dataimport is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('tournai.urban.dataimport'))

    def test_uninstall(self):
        """Test if tournai.urban.dataimport is cleanly uninstalled."""
        self.installer.uninstallProducts(['tournai.urban.dataimport'])
        self.assertFalse(self.installer.isProductInstalled('tournai.urban.dataimport'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ITournaiUrbanDataimportLayer is registered."""
        from tournai.urban.dataimport.interfaces import ITournaiUrbanDataimportLayer
        from plone.browserlayer import utils
        self.failUnless(ITournaiUrbanDataimportLayer in utils.registered_layers())
