from odoo import fields, models


class Material(models.Model):
    _name = "material"
    _description = "material request"

    material_line_ids = fields.One2many('material.order.line', 'material_id',
                                        string="Requests")
    state = fields.Selection([('new', 'New'), ('to_approve', 'To Approve'),
                              ('2nd_approval', 'Second Approval'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected')],
                             default='new', string="Status")
    purchase_id = fields.Many2one('purchase.order')

    def action_request(self):
        self.state = 'to_approve'
        products = []
        seller = []
        for rec in self.material_line_ids:
            if rec.type == "po":
                seller.append(rec.product_id.seller_ids.name[0].id)
                products.append(rec)
        seller = list(set(seller))
        print(products)
        print(seller)

        for sel in seller:
            purchase_vals = {
                'order_line': [],
                'partner_id': sel,
            }
            for pdt in products:
                if sel == pdt.product_id.seller_ids.name[0].id:
                    print("v_id----", sel)
                    print("p_id-----", pdt.product_id.seller_ids.name[0].id)
                    purchase_order = {
                        'product_id': pdt.product_id.id,
                        'price_unit': pdt.unit_cost,
                        'product_qty': pdt.material_quantity,
                    }
                    purchase_vals['order_line'].append((0, 0, purchase_order))
            print(purchase_vals)
            self.purchase_id = self.env['purchase.order'].create(purchase_vals)

    def action_approve_manager(self):
        self.state = '2nd_approval'

    def action_approve_head(self):
        self.state = 'approved'

    def action_reject_head(self):
        self.state = 'rejected'


class MaterialOrderLine(models.Model):
    _name = "material.order.line"

    product_id = fields.Many2one('product.product')
    unit_cost = fields.Float(string="Cost",
                             related='product_id.standard_price')
    material_id = fields.Many2one('material')
    material_quantity = fields.Float(string="Quantity", default='1')
    type = fields.Selection([('po', 'Purchase Order'),
                             ('internal_transfer', 'Internal Transfer')],
                            string="Request Type")
