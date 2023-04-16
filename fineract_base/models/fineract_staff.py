# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FineractUser(models.Model):
    _name = "fineract.staff"
    _description = "Fineract Staff"

    name = fields.Char()
