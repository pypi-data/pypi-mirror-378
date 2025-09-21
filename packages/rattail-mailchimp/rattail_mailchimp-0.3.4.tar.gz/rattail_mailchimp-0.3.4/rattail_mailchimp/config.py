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
Config extensions for rattail-mailchimp
"""

from wuttjamaican.conf import WuttaConfigExtension


class MailchimpConfigExtension(WuttaConfigExtension):
    """
    Config extension for rattail-mailchimp
    """
    key = 'rattail_mailchimp'

    def configure(self, config):

        # rattail import-mailchimp
        config.setdefault('rattail.importing', 'to_rattail.from_mailchimp.import.default_handler',
                          'rattail_mailchimp.importing.mailchimp:FromMailChimpToRattail')
        config.setdefault('rattail.importing', 'to_rattail.from_mailchimp.import.default_cmd',
                          'rattail import-mailchimp')
