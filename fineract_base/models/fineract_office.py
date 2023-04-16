# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models

PATH_ITEM_SEPARATOR = "\\"


class FineractUser(models.Model):
    _name = "fineract.office"
    _description = "Fineract Office"
    _parent_store = True

    name = fields.Char(required=True)
    parent_id = fields.Many2one("fineract.office", index=True)
    child_ids = fields.One2many("fineract.office", "parent_id", string="Branch Offices")
    parent_path = fields.Char(index=True, unaccent=False)
    complete_name = fields.Char(
        string="Full Path", compute="_compute_complete_name", recursive=True
    )
    opened_on = fields.Date(required=True)
    external_id = fields.Integer(compute="_compute_external_id", store=True)

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for office in self:
            office.complete_name = office._get_name_recursively()

    def _get_name_recursively(self, level=5):
        if level <= 0:
            return "..."
        if self.parent_id:
            return (
                self.parent_id._get_name_recursively(level - 1)
                + PATH_ITEM_SEPARATOR
                + (self.name or "")
            )
        else:
            return self.name

    @api.depends("name")
    def _compute_external_id(self):
        for office in self:
            office.external_id = office.id

    @api.model_create_multi
    def create(self, lst):
        first_record = True
        for vals in lst:
            # Only the first record must not have a parent_id. All others must have parents.
            if first_record:
                first_record = self.search_count([]) == 0
            if not first_record and "parent_id" not in vals:
                raise exceptions.ValidationError(
                    f"Only the first {self._name} record may have an empty parent_id field"
                )

        return super().create(lst)
