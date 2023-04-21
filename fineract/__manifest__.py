# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

# pylint: disable=pointless-statement
{
    "name": "Fineract",
    "summary": "Apache Fineract, A Platform for Microfinance",
    "version": "16.0.1.0.0",
    "category": "Fineract",
    "author": "Michael Telahun Makonnen, Trevi Software",
    "license": "AGPL-3",
    "website": "https://github.com/trevi-software/fineract-frontend",
    "depends": [
        "base",
    ],
    "data": [
        "data/ir_module_category.xml",
        "security/groups.xml",
        "views/fineract_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": True,
}
