# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Web Menus
"""

from tailbone import menus as base


class TutorialMenuHandler(base.MenuHandler):
    """
    Demo menu handler
    """

    def make_menus(self, request, **kwargs):

        products_menu = self.make_products_menu(request)

        vendors_menu = self.make_vendors_menu(request)

        company_menu = self.make_company_menu(request)

        batches_menu = self.make_batches_menu(request)

        admin_menu = self.make_admin_menu(request,
                                          include_stores=False,
                                          include_tenders=False)

        menus = [
            products_menu,
            vendors_menu,
            company_menu,
            batches_menu,
            admin_menu,
        ]

        return menus

    def make_products_menu(self, request, **kwargs):
        return {
            'title': "Products",
            'type': 'menu',
            'items': [
                {
                    'title': "Products",
                    'route': 'products',
                    'perm': 'products.list',
                },
                {
                    'title': "Brands",
                    'route': 'brands',
                    'perm': 'brands.list',
                },
                {
                    'title': "Report Codes",
                    'route': 'reportcodes',
                    'perm': 'reportcodes.list',
                },
            ],
        }

    def make_vendors_menu(self, request, **kwargs):
        return {
            'title': "Vendors",
            'type': 'menu',
            'items': [
                {
                    'title': "Vendors",
                    'route': 'vendors',
                    'perm': 'vendors.list',
                },
                {'type': 'sep'},
                {
                    'title': "Catalogs",
                    'route': 'vendorcatalogs',
                    'perm': 'vendorcatalogs.list',
                },
                {
                    'title': "Upload New Catalog",
                    'route': 'vendorcatalogs.create',
                    'perm': 'vendorcatalogs.create',
                },
            ],
        }

    def make_company_menu(self, request, **kwargs):
        return {
            'title': "Company",
            'type': 'menu',
            'items': [
                {
                    'title': "Stores",
                    'route': 'stores',
                    'perm': 'stores.list',
                },
                {
                    'title': "Departments",
                    'route': 'departments',
                    'perm': 'departments.list',
                },
                {
                    'title': "Subdepartments",
                    'route': 'subdepartments',
                    'perm': 'subdepartments.list',
                },
                {'type': 'sep'},
                {
                    'title': "Employees",
                    'route': 'employees',
                    'perm': 'employees.list',
                },
                {'type': 'sep'},
                {
                    'title': "Customers",
                    'route': 'customers',
                    'perm': 'customers.list',
                },
                {
                    'title': "Customer Groups",
                    'route': 'customergroups',
                    'perm': 'customergroups.list',
                },
            ],
        }

    def make_batches_menu(self, request, **kwargs):
        return {
            'title': "Batches",
            'type': 'menu',
            'items': [
                {
                    'title': "Handheld",
                    'route': 'batch.handheld',
                    'perm': 'batch.handheld.list',
                },
                {
                    'title': "Inventory",
                    'route': 'batch.inventory',
                    'perm': 'batch.inventory.list',
                },
            ],
        }
