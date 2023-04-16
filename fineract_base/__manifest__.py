# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

# pylint: disable=pointless-statement
{
    "name": "Fineract Base",
    "summary": "Basic Fineract front-end functionality.",
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
        "security/ir.model.access.csv",
    ],
    "external_dependencies": {
        "python": ["cryptography"],
    },
    "installable": True,
}
