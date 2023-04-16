# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from psycopg2.errors import NotNullViolation

from odoo.exceptions import ValidationError

from .common import TestFineractBase


class TestOffice(TestFineractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_office_required_fields(self):
        head_office = self.FineractOffice.create(
            {"name": "Head Office", "opened_on": date(2023, 1, 1)}
        )

        error_cases = [
            (
                {
                    "parent_id": head_office.id,
                    "opened_on": date(2023, 1, 1),
                },
                NotNullViolation,
                "missing name",
            ),
            (
                {
                    "name": "Rome Office",
                    "parent_id": head_office.id,
                },
                NotNullViolation,
                "missing opened date",
            ),
            (
                {
                    "name": "Rome Office",
                    "opened_on": date(2023, 1, 1),
                },
                ValidationError,
                "missing parent",
            ),
        ]
        for (case, ex, _msg) in error_cases:
            with self.assertRaises(ex):
                self.FineractOffice.create(case)

    def test_complete_name(self):
        l1_taxonomy = {
            "name": "Species",
            "opened_on": date(2023, 1, 1),
        }
        l1 = self.FineractOffice.create(l1_taxonomy)
        l2_taxonomy = {
            "name": "Genus",
            "opened_on": date(2023, 1, 1),
            "parent_id": l1.id,
        }
        l2 = self.FineractOffice.create(l2_taxonomy)
        l3_taxonomy = {
            "name": "Family",
            "opened_on": date(2023, 1, 1),
            "parent_id": l2.id,
        }
        l3 = self.FineractOffice.create(l3_taxonomy)
        l4_taxonomy = {
            "name": "Order",
            "opened_on": date(2023, 1, 1),
            "parent_id": l3.id,
        }
        l4 = self.FineractOffice.create(l4_taxonomy)
        l5_taxonomy = {
            "name": "Class",
            "opened_on": date(2023, 1, 1),
            "parent_id": l4.id,
        }
        l5 = self.FineractOffice.create(l5_taxonomy)
        l6_taxonomy = {
            "name": "Phylum",
            "opened_on": date(2023, 1, 1),
            "parent_id": l5.id,
        }
        l6 = self.FineractOffice.create(l6_taxonomy)

        self.assertEqual(
            l1.complete_name,
            "Species",
            "Complete name without parents shows only the current name",
        )
        self.assertEqual(
            l5.complete_name,
            "Species\\Genus\\Family\\Order\\Class",
            "At 5 levels of parents the complete name is displayed",
        )
        self.assertEqual(
            l6.complete_name,
            "...\\Genus\\Family\\Order\\Class\\Phylum",
            "After 6 levels of parents an abbreviated complete name is displayed",
        )

    def test_computed_external_id(self):
        vals = {
            "name": "Head Office",
            "opened_on": date(2023, 1, 1),
        }
        ho = self.FineractOffice.create(vals)

        self.assertEqual(ho.external_id, ho.id, "External ID is same as Id")
