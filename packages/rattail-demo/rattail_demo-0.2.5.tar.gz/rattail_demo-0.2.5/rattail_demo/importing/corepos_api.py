# -*- coding: utf-8; -*-
"""
CORE-POS API -> Rattail Demo importing
"""

from rattail_corepos.importing.corepos import api as base


class FromCOREPOSToRattail(base.FromCOREPOSToRattail):
    """
    Override some parts of CORE-POS API -> Rattail importing.
    """

    def get_importers(self):
        importers = super(FromCOREPOSToRattail, self).get_importers()
        importers['Store'] = StoreImporter
        return importers


class StoreImporter(base.StoreImporter):
    """
    Tweak how we import Store data from CORE-POS API.
    """

    def cache_query(self):
        model = self.model
        # we ignore any Store records which are not associated with CORE, so
        # the importer will never be tempted to delete them etc.
        return self.session.query(model.Store)\
                           .join(model.CoreStore)\
                           .filter(model.CoreStore.corepos_id != None)
