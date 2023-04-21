# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo.tests import new_test_user

from .common import TestFineractBase


class TestAccess(TestFineractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.headOffice = cls.FineractOffice.create(
            {
                "name": "Head Office",
                "opened_on": date(2021, 1, 1),
            }
        )

        # Normal User John
        cls.userJohn = new_test_user(
            cls.env,
            login="john1",
            groups="base.group_user,fineract.group_fineract_user",
            name="John",
        )

        # Fineract Manager
        cls.userFM = new_test_user(
            cls.env,
            login="finmgr",
            groups="base.group_user,fineract.group_fineract_manager",
            name="Fineract manager",
            email="fm@example.com",
            company_ids=[(6, 0, cls.env.companies.ids)],
        )

    def test_user_access(self):
        """fineract.user access: FM - full access, normal user - no access"""

        # FM
        user_data = self.fineract_user_sample_values.copy()
        user_data.update(
            {
                "username": self.userFM.login,
                "odoo_user_id": self.userFM.id,
                "office_id": self.headOffice.id,
            }
        )
        sample = self.create_succeeds(self.userFM, self.FineractUser, user_data)
        self.read_succeeds(self.userFM, self.FineractUser, sample.id)
        self.write_succeeds(
            self.userFM, self.FineractUser, sample.id, {"username": "tba"}
        )
        self.unlink_succeeds(self.userFM, sample)

        # User
        user_data = self.fineract_user_sample_values.copy()
        user_data.update(
            {
                "username": self.userJohn.login,
                "odoo_user_id": self.userJohn.id,
                "office_id": self.headOffice.id,
            }
        )
        sample = self.FineractUser.create(user_data)
        self.create_fails(self.userJohn, self.FineractUser, user_data)
        self.read_succeeds(self.userJohn, self.FineractUser, sample.id)
        self.write_fails(
            self.userJohn, self.FineractUser, sample.id, {"username": "tba"}
        )
        self.unlink_fails(self.userJohn, sample)

    def test_own_user_access(self):
        """A user can only read his/her own fineract user record"""

        fin_user_data_FM = self.fineract_user_sample_values.copy()
        fin_user_data_FM.update(
            {
                "username": self.userFM.login,
                "odoo_user_id": self.userFM.id,
                "office_id": self.headOffice.id,
            }
        )
        fin_user_FM = self.FineractUser.with_user(self.userFM).create(fin_user_data_FM)

        fin_user_data_John = self.fineract_user_sample_values.copy()
        fin_user_data_John.update(
            {
                "username": self.userJohn.login,
                "odoo_user_id": self.userJohn.id,
                "office_id": self.headOffice.id,
            }
        )
        fin_user_John = self.FineractUser.with_user(self.userFM).create(
            fin_user_data_John
        )

        grpMgr = self.env.ref("fineract.group_fineract_manager")
        self.assertNotIn(grpMgr, self.userJohn.groups_id)
        grpUser = self.env.ref("fineract.group_fineract_user")
        self.assertIn(grpUser, self.userJohn.groups_id)

        # John can read his linked fineract user record
        self.read_succeeds(self.userJohn, self.FineractUser, fin_user_John.id)
        # but not Others'
        self.read_fails(self.userJohn, self.FineractUser, fin_user_FM.id)
        # John can't modify his linked fineract user or Others'
        self.write_fails(
            self.userJohn, self.FineractUser, fin_user_John.id, {"first_name": "A"}
        )
        self.write_fails(
            self.userJohn, self.FineractUser, fin_user_FM.id, {"first_name": "A"}
        )
