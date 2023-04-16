# Copyright (C) 2023 Michael Telahun Makonnen <mtm@trevi.et>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from odoo import _, api, exceptions, fields, models

PARAM_PASS = "itm_passkey"
PARAM_SALT = "itm_salt"
MIN_USERNAME = 5


class FineractUser(models.Model):
    _name = "fineract.user"
    _description = "Fineract User"
    _order_by = "first_name,last_name"

    odoo_user_id = fields.Many2one("res.users", required=True)
    username = fields.Char(required=True)
    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    email = fields.Char(required=True)
    password = fields.Char(
        compute="_compute_password",
        inverse="_inverse_set_password",
        copy=False,
        invisible=True,
        store=True,
    )
    overide_password_expiry_policy = fields.Boolean()
    office_id = fields.Many2one("fineract.office", required=True)
    staff_id = fields.Many2one("fineract.staff")
    role_ids = fields.One2many(
        comodel_name="fineract.role", inverse_name="fineract_user_id"
    )

    def _compute_password(self):
        for fineract_user in self:
            fineract_user.password = ""

    def _inverse_set_password(self):
        for fineract_user in self:
            self._set_encrypted_password(
                fineract_user.id, self.encrypt_string(fineract_user.password)
            )

    @api.model
    def _set_encrypted_password(self, res_id, encrypted_pw):
        self.env.cr.execute(
            "UPDATE fineract_user SET password=%s WHERE id=%s",
            (encrypted_pw.decode("utf-8"), res_id),
        )
        self.browse(res_id).invalidate_recordset(["password"])

    @api.model
    def encrypt_string(self, plaintext):
        """Returns a URL-safe string containing the encrypted version of plaintext."""

        key = self.get_urlsafe_key()
        f = Fernet(key)
        cipher = f.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(cipher)

    def decrypt_password_as_string(self):
        """Returns a string representing the plaintext password in record.
        Returns empty string if the password is not set."""

        self.ensure_one()

        key = self.get_urlsafe_key()
        f = Fernet(key)

        plaintext = ""
        self.env.cr.execute(
            "SELECT password FROM fineract_user WHERE id=%s", (self.id,)
        )
        res = self.env.cr.dictfetchone()
        if res["password"] is not None:
            token = base64.urlsafe_b64decode(res["password"])
            plaintext = f.decrypt(token).decode()
        return plaintext

    def get_urlsafe_key(self):

        ConfigParam = self.env["ir.config_parameter"]
        salt = None
        passphrase = ConfigParam.sudo().get_param(PARAM_PASS)
        if not passphrase:
            passphrase = base64.urlsafe_b64encode(os.urandom(64)).decode()
            salt = os.urandom(16)
            ConfigParam.sudo().set_param(PARAM_PASS, passphrase)
            ConfigParam.sudo().set_param(
                PARAM_SALT, base64.urlsafe_b64encode(salt).decode()
            )
        else:
            salt = base64.urlsafe_b64decode(
                ConfigParam.sudo().get_param(PARAM_SALT).encode()
            )

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

    @api.model_create_multi
    def create(self, lst):
        for vals in lst:
            username = vals.get("username")
            if username is not None and len(username) < MIN_USERNAME:
                raise exceptions.ValidationError(
                    _("username must be at least 5 characters long")
                )

        return super().create(lst)

    def write(self, vals):
        if "password" in vals.keys() and vals["password"] is not False:
            vals["password"] = self.encrypt_string(vals["password"])

        return super().write(vals)
