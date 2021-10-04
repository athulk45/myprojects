from odoo import fields, models, api


class BookReservation(models.Model):
    _name = "book.reservation"
    _description = "Book reservation"
    _rec_name = "reservation_seq"

    scholar_id = fields.Many2one('research.scholar', string="Scholar")
    book_ids = fields.One2many('book.order.line', 'book_id')
    responsible_id = fields.Many2one('res.users', string="Responsible",
                                     readonly=True,
                                     default=lambda self: self.env.user)
    state = fields.Selection([('new', 'New'), ('approval', 'To Approve'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected'),
                              ('invoiced', 'Invoiced')],
                             default='new', string="Status")
    reservation_seq = fields.Char(string='Serial Number', required=True,
                                  copy=False,
                                  readonly=True, default=lambda self: 'New')
    invoice_id = fields.Many2one('account.move')
    today_date = fields.Date(default=fields.Date.today())

    def action_submit(self):
        self.state = 'approval'

    def action_cancel(self):
        self.state = 'new'

    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'

    def action_invoice(self):
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.scholar_id.partner_id,
            'invoice_date': self.today_date,
            'invoice_line_ids': [],
        }
        for rec in self.book_ids.product_id:
            invoice_line_vals = {
                'name': rec.name,
                'product_id': rec.id,
                'price_unit': rec.lst_price,
            }

            invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))
        self.invoice_id = self.env['account.move'].create(invoice_vals)
        print(self.invoice_id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'target': 'current'
        }

    @api.model
    def create(self, val):
        if val.get('reservation_seq', 'New' == 'New'):
            val['reservation_seq'] = self.env['ir.sequence'].next_by_code(
                'book.reservation')
            return super(BookReservation, self).create(val)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    book_ok = fields.Boolean(default=False)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    reservation_id = fields.Many2one('book.reservation',
                                     string="Book Reservation")

    @api.onchange('reservation_id')
    def onchange_reservation_id(self):

        for rec in self:
            lines = [(5, 0)]
            for i in self.reservation_id.book_ids.product_id:
                val = {
                    'product_id': i.id,
                    'name': i.name,
                    'price_unit': i.lst_price,
                }
                lines.append([0, 0, val])
            rec.order_line = lines
            if self.reservation_id:
                self.partner_id = self.reservation_id.scholar_id.partner_id


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        sale = self.env['book.reservation'].search(
            [('invoice_id.id', '=', self.id)])
        sale.state = 'invoiced'
        return super(AccountMove, self).action_post()


class BookOrderLine(models.Model):
    _name = "book.order.line"

    product_id = fields.Many2one('product.product')
    unit_price = fields.Float(string="Price",
                              related='product_id.lst_price')
    book_id = fields.Many2one('book.reservation')
    default_code = fields.Char(string="Internal Reference",
                               related='product_id.default_code')
