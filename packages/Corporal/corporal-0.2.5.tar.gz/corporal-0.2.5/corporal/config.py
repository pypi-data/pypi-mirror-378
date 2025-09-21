# -*- coding: utf-8; -*-
"""
Custom config
"""

from wuttjamaican.conf import WuttaConfigExtension


class CorporalConfig(WuttaConfigExtension):
    """
    Rattail config extension for Corporal
    """
    key = 'corporal'

    def configure(self, config):

        if config.getbool('rattail.config', 'corporal.set_defaults',
                          usedb=False, default=True):

            # set some default config values
            config.setdefault('rattail', 'model', 'corporal.db.model')
            config.setdefault('tailbone.menus', 'handler', 'corporal.web.menus:CorporalMenuHandler')
            config.setdefault('rattail.config', 'templates', 'corporal:data/config rattail:data/config')

            # batches
            config.setdefault('rattail.batch.vendor_catalog.handler.spec', 'corporal.batch.vendorcatalog:VendorCatalogHandler')
