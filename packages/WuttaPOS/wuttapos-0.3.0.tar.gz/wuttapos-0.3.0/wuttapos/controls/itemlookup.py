# -*- coding: utf-8; -*-
################################################################################
#
#  WuttaPOS -- Pythonic Point of Sale System
#  Copyright © 2023 Lance Edgar
#
#  This file is part of WuttaPOS.
#
#  WuttaPOS is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  WuttaPOS is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  WuttaPOS.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
WuttaPOS - item lookup control
"""

from .lookup import WuttaLookup


class WuttaProductLookup(WuttaLookup):

    def get_results_columns(self):
        return [
            self.app.get_product_key_label(),
            "Description",
            "Price",
        ]

    def get_results(self, session, entry):
        return self.app.get_products_handler().search_products(session, entry)

    def make_result_row(self, product):
        return [
            product['product_key'],
            product['full_description'],
            product['unit_price_display'],
        ]
