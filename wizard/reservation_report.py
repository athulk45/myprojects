from odoo.exceptions import UserError
import json
import io
from odoo import fields, models
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


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
            query = query + " where s.partner_id = '%d' and b.create_date>" \
                            "'%s'and b.create_date<'%s'" % (self.customer_id,
                                                        self.from_date,
                                                        self.to_date)
        elif self.customer_id:
            query = query + " where s.partner_id = '%d'" % self.customer_id

        elif self.book_ids and self.from_date and self.to_date:
            query = query + " where o.product_id in " + products + \
                    "and b.create_date>'%s' and b.create_date<'%s'" % (
                        self.from_date, self.to_date)
        elif self.book_ids:
            query = query + " where o.product_id in" + products

        elif self.from_date and self.to_date:
            query = query + " where b.create_date>'%s'and b.create_date<'%s'" \
                    % (self.from_date, self.to_date)
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        print(result)
        print(self.read())
        data = {
            'form': self.read()[0],
            'record': result,
        }
        return self.env.ref(
            'reserarch_management.action_report_reservation').report_action(
            self, data=data)

    """---------------------------------------------------------------------"""

    def get_excel_report(self):
        print("hi")
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
            query = query + " where s.partner_id = '%d' and b.create_date>" \
                            "'%s' and b.create_date<'%s'" % (self.customer_id,
                                                        self.from_date,
                                                        self.to_date)
        elif self.customer_id:
            query = query + " where s.partner_id = '%d'" % self.customer_id

        elif self.book_ids and self.from_date and self.to_date:
            query = query + " where o.product_id in " + products + \
                    "and b.create_date>'%s' and b.create_date<'%s'" % (
                        self.from_date,
                        self.to_date)
        elif self.book_ids:
            query = query + " where o.product_id in" + products

        elif self.from_date and self.to_date:
            query = query + " where b.create_date>'%s'and b.create_date<'%s'" \
                    % (self.from_date, self.to_date)
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        print(result)
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'record': result
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'reservation.report',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Excel Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': '12px'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        txt = workbook.add_format({'font_size': '10px'})
        sheet.merge_range('B2:J3', 'Book Reservation Report', head)
        sheet.write('B6', 'From:', cell_format)
        sheet.merge_range('C6:D6', data['from_date'], txt)
        sheet.write('H6', 'To:', cell_format)
        sheet.merge_range('I6:J6', data['to_date'], txt)
        format1 = workbook.add_format(
            {'font_size': 10, 'align': 'left'})
        format2 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'bold': True,
             'bg_color': '#6BA6FE', 'border': 1})

        row = 8
        col = 2
        sheet.write(row, col, 'Sl No.', format2)
        col += 1
        sheet.write(row, col, 'Reference', format2)
        col += 1
        # sheet.merge_range('D9:E9', 'Book', format2)
        sheet.write(row, col, 'Book', format2)
        col += 1
        # sheet.merge_range('F9:G9', 'Reserved Date', format2)
        sheet.write(row, col, 'Reserved Date', format2)
        col += 1
        # sheet.merge_range('H9:I9', 'Customer', format2)
        sheet.write(row, col, 'Customer', format2)
        col += 1
        sheet.write(row, col, 'Status', format2)
        col += 1
        row_number = 9
        i = 0
        for val in data['record']:
            column_number = 2
            i += 1
            sheet.write(row_number, column_number, i, format1)
            column_number += 1
            sheet.write(row_number, column_number, val['reservation_seq'],
                        format1)
            column_number += 1
            sheet.write(row_number, column_number, val['name'], format1)
            column_number += 1
            sheet.write(row_number, column_number, val['create_date'], format1)
            column_number += 1
            sheet.write(row_number, column_number, val['display_name'], format1)
            column_number += 1
            sheet.write(row_number, column_number, val['state'], format1)
            column_number += 1
            row_number += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
