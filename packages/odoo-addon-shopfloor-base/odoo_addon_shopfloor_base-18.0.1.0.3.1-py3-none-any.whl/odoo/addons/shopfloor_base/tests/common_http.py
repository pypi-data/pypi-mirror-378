# Copyright 2022 Camptocamp SA (http://www.camptocamp.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
import unittest

import requests

from odoo.tests import HttpCase

from odoo.addons.base_rest.tests.common import RegistryMixin
from odoo.addons.component.tests.common import ComponentMixin


@unittest.skipIf(os.getenv("SKIP_HTTP_CASE"), "HttpCase skipped")
class HttpCommonCase(HttpCase, RegistryMixin, ComponentMixin):
    """Common class for testing endpoints.

    Testing services is very good for unit/integration testing.
    Testing that those services and their methods are properly exposed
    via automatic controllers is very important as well.

    Use this class to make sure your services are working as expected.
    """

    tracking_disable = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=cls.tracking_disable,
            )
        )
        cls.setUpComponent()
        cls.setUpRegistry()
        cls.setUpClassBaseData()
        # Keep this here to have the whole env set up already
        cls.setUpShopfloorApp()

    @classmethod
    def setUpClassBaseData(cls):
        pass

    @classmethod
    def setUpShopfloorApp(cls):
        cls.shopfloor_app = cls.env["shopfloor.app"].create(
            {
                "tech_name": "http_test",
                "name": "HTTP Test",
                "short_name": "HTTP test",
            }
        )

    # pylint: disable=method-required-super
    # super is called "the old-style way" to call both super classes in the
    # order we want
    def setUp(self):
        # Have to initialize both odoo env and stuff +
        # the Component registry of the mixin
        HttpCase.setUp(self)
        ComponentMixin.setUp(self)
        # Make sure endpoints are available
        self.shopfloor_app._handle_registry_sync()

    def _make_url(self, route):
        return f"{self.base_url()}/{route}"

    def _make_request(self, route, api_key=None, menu=None, profile=None, headers=None):
        # use requests because you cannot easily manipulate the request w/ `url_open`
        headers = headers or {}
        if api_key:
            headers["API-KEY"] = api_key.key
        if menu:
            headers["SERVICE-CTX-MENU-ID"] = str(menu.id)
        if profile:
            headers["SERVICE-CTX-PROFILE-ID"] = str(profile.id)
        return requests.get(self._make_url(route), headers=headers, timeout=10)
