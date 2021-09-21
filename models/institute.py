from odoo import fields, models


class Institute(models.Model):
    _name = "research.institute"
    _description = "institution"

    name = fields.Char(string="Name")
    address = fields.Text(string="Address")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
