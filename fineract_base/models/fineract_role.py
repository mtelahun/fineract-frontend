# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FineractUser(models.Model):
    _name = "fineract.role"
    _description = "Fineract Role"

    name = fields.Char()
    fineract_user_id = fields.Many2one("fineract.user")
