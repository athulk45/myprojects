from odoo import models, fields
from odoo.exceptions import UserError


class ReservationReport(models.TransientModel):
    _name = "reservation.report"

    book_ids = fields.Many2many('product.template', string="Books")
    customer_id = fields.Many2one('res.partner', string="Customer")
    from_date = fields.Date(string="Date From")
    to_date = fields.Date(string="From To")

    def get_report(self):
        print(self.from_date)
        print(self.customer_id)
        if self.book_ids and self.customer_id:
            raise UserError("select either product or customer")
        products = str(self.book_ids.mapped('id'))
        products = '(' + products[1:-1] + ')'
        print(products)
        query = 'SELECT b.reservation_seq,b.create_date,b.state,p.name,' \
                'r.display_name from' \
                ' book_reservation as b INNER JOIN book_order_line as o ON' \
                ' o.book_id = b.id INNER JOIN product_template as p ON ' \
                'o.product_id = p.id INNER JOIN research_scholar as s ON' \
                ' b.scholar_id = s.id INNER JOIN res_partner r ON' \
                ' s.partner_id = r.id'

        if self.customer_id and self.from_date and self.to_date:
            query = query + " where s.partner_id = '%d' and b.create_date>'%s'" \
                            "and b.create_date<'%s'" % (self.customer_id,
                                                        self.from_date,
                                                        self.to_date)
        elif self.customer_id:
            query = query + " where s.partner_id = '%d'" % self.customer_id

        elif self.book_ids and self.from_date and self.to_date:
            query = query + " where o.product_id in " + products + "and b.create_date>'%s'" \
                                "and b.create_date<'%s'" % (self.from_date,
                                                            self.to_date)
        elif self.book_ids :
            query = query + " where o.product_id in" + products

        elif self.from_date and self.to_date:
            query = query + " where b.create_date>'%s'and b.create_date<'%s'" \
                    % (self.from_date, self.to_date)
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        print(result)
        data = {
            'form': self.read()[0],
            'record': result,
        }
        return self.env.ref(
            'reserarch_management.action_report_reservation').report_action(
            self, data=data)

# temp_list = str(self.sale_person_ids.mapped('id'))
# temp_list = '(' + temp_list[1:-1] + ')'
# print(temp_list)
# query = 'SELECT co.commission, so.amount_total, res.name as person, ' \
#         'crm.name as team FROM commission_information co INNER JOIN ' \
#         'sale_order so ON co.sale_id = so.id INNER JOIN res_users ru ' \
#         'ON co.user_id = ru.id INNER JOIN res_partner res ON ' \
#         'ru.partner_id = res.id INNER JOIN crm_team crm ON ' \
#         'so.team_id = crm.id '
# if self.sale_person_ids and self.sale_team_id and self.from_date \
#         and self.to_date:
#     query = query + "where co.user_id in "+temp_list + \
#             "and so.team_id = '%d' and so.date_order>'%s' " \
#             "and so.date_order <'%s'" \
#             % (self.sale_team_id, self.from_date, self.to_date)
# elif self.sale_team_id and self.from_date and self.to_date:
#     query = query + " where so.team_id = '%d' and so.date_order>'%s' " \
#                     "and so.date_order<'%s'"\
#             % (self.sale_team_id, self.from_date, self.to_date)
# elif self.sale_person_ids and self.from_date and self.to_date:
#     query = query + " where co.user_id in "+temp_list +  \
#                     "and so.date_order>'%s' and so.date_order<'%s'" \
#             % (self.from_date, self.to_date)
# elif self.from_date and self.to_date:
#     query = query + " where so.date_order>'%s' and so.date_order<'%s'" \
#             % (self.from_date, self.to_date)
# self.env.cr.execute(query)
# result = self.env.cr.dictfetchall()
