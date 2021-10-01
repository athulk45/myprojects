from odoo import models, fields, _
from odoo.exceptions import UserError


class ReservationReport(models.TransientModel):
    _name = "reservation.report"

    book_ids = fields.Many2many('product.product', string="Books")
    customer_id = fields.Many2one('research.scholar', string="Scholar")
    from_date = fields.Date(string="Date From")
    to_date = fields.Date(string="From To")

    def get_report(self):
        print(self.book_ids)
        print(self.from_date)
        print(self.customer_id)
        if self.book_ids and self.customer_ids:
            raise UserError("select either product or customer")
        data = {
            'form': self.read()[0],
            'customer': self.customer_ids.partner_id,
        }
        print(data)
        return self.env.ref(
            'reserarch_management.action_report_reservation').report_action(
            self, data=data)

