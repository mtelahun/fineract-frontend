# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random
import string
from datetime import date

from odoo.exceptions import AccessError
from odoo.tests import common


class TestFineractBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestFineractBase, cls).setUpClass()

        cls.FineractOffice = cls.env["fineract.office"]
        cls.FineractRole = cls.env["fineract.role"]
        cls.FineractStaff = cls.env["fineract.staff"]
        cls.FineractUser = cls.env["fineract.user"]
        cls.ResUsers = cls.env["res.users"]

        # fineract.user - sample values
        cls.fineract_user_sample_values = {
            "email": "alice@example.org",
            "first_name": "Alice",
            "last_name": "Alison",
        }

    def new_test_fineract_user(self, password=None, head_office_id=None):
        username = "".join(random.choices(string.ascii_lowercase, k=8))
        odoo_user = self.create_odoo_user({"login": username, "name": username})
        user_values = self.fineract_user_sample_values.copy()
        if password is not None:
            user_values.update({"password": password})
        if head_office_id is None:
            head_office = self.FineractOffice.create(
                {"name": "Head Office", "opened_on": date(2023, 1, 1)}
            )
            head_office_id = head_office.id

        return self.new_test_fineract_user_with_values(
            username, odoo_user.id, head_office_id, user_values
        )

    def new_test_fineract_user_with_values(
        self, username, odoo_user_id, head_office_id, vals
    ):
        vals.update(
            {
                "username": username,
                "odoo_user_id": odoo_user_id,
                "office_id": head_office_id,
            }
        )
        return self.FineractUser.create(vals)

    def create_odoo_user(self, vals):
        return self.ResUsers.create(vals)

    def create_fails(self, user, obj, vals):
        with self.assertRaises(AccessError):
            obj.with_user(user).create(vals)

    def create_succeeds(self, user, obj, vals):
        res = None
        try:
            res = obj.with_user(user).create(vals)
        except AccessError:
            self.fail("Caught unexpected exception creating {}".format(obj._name))
        return res

    def unlink_fails(self, user, obj):
        with self.assertRaises(AccessError):
            obj.with_user(user).unlink()

    def unlink_succeeds(self, user, obj):
        try:
            obj.with_user(user).unlink()
        except AccessError:
            self.fail("Caught unexpected exception unlinking {}".format(obj._name))

    def read_succeeds(self, user, obj, obj_id):
        try:
            obj.with_user(user).browse(obj_id).read([])
        except AccessError:
            self.fail("Caught an unexpected exception reading {}".format(obj._name))

    def read_fails(self, user, obj, obj_id):
        with self.assertRaises(AccessError):
            obj.with_user(user).browse(obj_id).read([])

    # Pre-requisite: READ Access
    def write_fails(self, user, obj, obj_id, write_vals):
        with self.assertRaises(AccessError):
            obj.with_user(user).browse(obj_id).write(write_vals)

    # Pre-requisite: READ Access
    def write_succeeds(self, user, obj, obj_id, write_vals):
        try:
            obj.with_user(user).browse(obj_id).write(write_vals)
        except AccessError:
            self.fail("Caught an unexpected exception writing {}".format(obj._name))
