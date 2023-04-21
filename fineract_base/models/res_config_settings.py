# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fineract_uri = fields.Char(
        string="Fineract URI",
        config_parameter="fineract_backend.fineract_uri",
        default=False,
        help="The URI of the Fineract backend (example: https://localhost:8443/)",
    )
    tenant_id = fields.Char(
        config_parameter="fineract_backend.tenant_id",
        default="default",
        help="The ID of the tenant to connect as in the Fineract backend.",
    )
