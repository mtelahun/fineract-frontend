# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from psycopg2.errors import NotNullViolation

from odoo.exceptions import ValidationError

from .common import TestFineractBase


class TestAccess(TestFineractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.head_office = cls.FineractOffice.create(
            {
                "name": "Head Office",
                "opened_on": date(2023, 1, 1),
            }
        )

    def test_user_required_fields(self):
        odoo_user = self.create_odoo_user({"login": "sally", "name": "Sally"})
        error_cases = [
            (
                {
                    "email": "testuser@example.org",
                    "first_name": "Alice",
                    "last_name": "Robertson",
                    "odoo_user_id": odoo_user.id,
                    "office_id": self.head_office.id,
                },
                NotNullViolation,
                "missing username",
            ),
            (
                {
                    "username": "testuser",
                    "first_name": "Alice",
                    "last_name": "Robertson",
                    "odoo_user_id": odoo_user.id,
                    "office_id": self.head_office.id,
                },
                NotNullViolation,
                "missing email",
            ),
            (
                {
                    "username": "testuser",
                    "email": "testuser@example.org",
                    "last_name": "Robertson",
                    "odoo_user_id": odoo_user.id,
                    "office_id": self.head_office.id,
                },
                NotNullViolation,
                "missing first name",
            ),
            (
                {
                    "username": "testuser",
                    "email": "testuser@example.org",
                    "first_name": "Alice",
                    "odoo_user_id": odoo_user.id,
                    "office_id": self.head_office.id,
                },
                NotNullViolation,
                "missing last name",
            ),
            (
                {
                    "username": "testuser",
                    "email": "testuser@example.org",
                    "first_name": "Alice",
                    "last_name": "Robertson",
                    "office_id": self.head_office.id,
                },
                NotNullViolation,
                "missing Odoo user_id",
            ),
            (
                {
                    "username": "testuser",
                    "email": "testuser@example.org",
                    "first_name": "Alice",
                    "last_name": "Robertson",
                    "odoo_user_id": odoo_user.id,
                },
                NotNullViolation,
                "missing Office",
            ),
        ]
        for (case, ex, _msg) in error_cases:
            with self.assertRaises(ex):
                self.FineractUser.create(case)

    def test_change_password(self):
        """Changing password results in encrypted version of new password"""

        cred = self.new_test_fineract_user("1111", self.head_office.id)
        pw = cred.decrypt_password_as_string()
        self.assertEqual("1111", pw, "Initial password was set correctly")

        cred.password = "456"
        cred.invalidate_recordset(["password"], flush=True)
        pw = cred.decrypt_password_as_string()
        self.assertEqual("456", pw, "New password was set correctly")

    def test_uniqueness(self):
        """Identical passwords have differing encrypted outputs"""

        cred1 = self.new_test_fineract_user("password", self.head_office.id)
        cred2 = self.new_test_fineract_user("password", self.head_office.id)
        strPass1 = cred1.decrypt_password_as_string()
        strPass2 = cred2.decrypt_password_as_string()
        self.assertEqual(strPass2, strPass1)

        self.env.cr.execute(
            "SELECT password from fineract_user WHERE id=%s", (cred1.id,)
        )
        token1 = self.env.cr.fetchone()[0]
        self.env.cr.execute(
            "SELECT password from fineract_user WHERE id=%s", (cred2.id,)
        )
        token2 = self.env.cr.fetchone()[0]
        self.assertNotEqual(
            token1,
            token2,
            "Password strings are identical but ciphertext should differ",
        )

    def test_unset_password(self):
        """Unset password returns empty string"""

        odoo_user = self.create_odoo_user({"login": "sally", "name": "Sally"})
        cred = self.new_test_fineract_user_with_values(
            "sally", odoo_user.id, self.head_office.id, self.fineract_user_sample_values
        )
        strRandom = cred.decrypt_password_as_string()
        self.assertEqual(0, len(strRandom))

    def test_username_length(self):
        odoo_user = self.create_odoo_user({"login": "sally", "name": "Sally"})
        with self.assertRaises(ValidationError):
            self.new_test_fineract_user_with_values(
                "m123",
                odoo_user.id,
                self.head_office.id,
                self.fineract_user_sample_values,
            )
