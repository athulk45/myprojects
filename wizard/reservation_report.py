import xlsxwriter
from xlrd import sheet
from xlsxwriter import workbook

from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools import json, date_utils
from json import *
import io


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
            query = query + " where s.partner_id = '%d' and b.create_date>'%s'" \
                            "and b.create_date<'%s'" % (self.customer_id,
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
            'id': self.id,
            'model': self._name,
            'from': self.from_date,
            'to_date': self.to_date,
            'table_data': result,
            'form': self.read()[0],
        }
        print(data)
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
        user_obj = self.env.user
        sheet = workbook.add_worksheet('Book Reservation Report')
        heading = workbook.add_format(
            {'font_size': 20, 'align': 'center', 'bold': True,
             'bg_color': '#D3D3D3', 'border': 1})
        format1 = workbook.add_format(
            {'font_size': 10, 'align': 'left'})
        heading = workbook.add_format(
            {'font_size': 20, 'align': 'center', 'bold': True,
            'bg_color': '#D3D3D3', 'border': 1})
        format1 = workbook.add_format(
            {'font_size': 10, 'align': 'left'})
            format2 = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'bold': True,
            'bg_color': '#D3D3D3', 'border': 1})
        sheet.set_column(0, 9, 20)
        sheet.write('B2', user_obj.company_id.name, format1)
        sheet.write('B3', user_obj.company_id.street, format1)
        sheet.write('B4', user_obj.company_id.city, format1)
        sheet.write('B5', user_obj.company_id.zip, format1)
        sheet.write('B6', user_obj.company_id.state_id.name, format1)
        sheet.write('B7', user_obj.company_id.country_id.name, format1)
        sheet.merge_range('B8:G9', "Accomodation Report", heading)

        if data['start_date']:
            sheet.write('B12', "Date From:", format2)
            sheet.write('C12', data['start_date'], format1)
        if data['end_date']:
            sheet.write('B13', "Date To:", format2)
            sheet.write('C13', data['end_date'], format1)
        if data['guest_id']:
            sheet.write('B14', 'Guest:', format2)
            sheet.write('C14', data['guest_id'], format1)
        if not data['start_date'] & data['end_date']:
            sheet.write('B13', "Date:", format2)
            sheet.write('C13', data['today_date'], format1)

        row = 15
        col = 1
        sheet.write(row, col, 'Sl No.', format2)
        col += 1
        sheet.write(row, col, 'Reference', format2)
        col += 1
        sheet.write(row, col, 'Room No', format2)
        col += 1
        sheet.write(row, col, 'Check In', format2)
        col += 1
        sheet.write(row, col, 'Check Out', format2)
        col += 1
        if not data['guest_id']:
            sheet.write(row, col, 'Guest', format2)
        col += 1
        row_number = 16
        i = 0
        for val in data['table_data']:
            column_number = 1
            i += 1
            sheet.write(row_number, column_number, i,
                    format1)
            column_number += 1
            sheet.write(row_number, column_number, val['accomodation_id'],
                        format1)
            column_number += 1
            sheet.write(row_number, column_number, val['room_no'], format1)
            column_number += 1
            sheet.write(row_number, column_number, val['check_in'], format1)
            column_number += 1
            sheet.write(row_number, column_number, val['check_out'], format1)
            column_number += 1


"""--------------------------------------------------------------------------"""





# def print_xlsx(self):
#     guest_id = self.guest_id.id
#     from_date = self.from_date
#     to_date = self.to_date
#     today_date = self.today_date
#     print(today_date)
#
#
#     query = 'SELECT acc.accomodation_id,acc.check_in,acc.check_out,' \
#             'res.name,num.room_no  FROM hotel_accomodation acc INNER JOIN ' \
#             'res_partner res ON (acc.guest_id = res.id) ' \
#             'INNER JOIN hotel_number num ON acc.room_id = num.id'
#     if guest_id and from_date and to_date:
#         query = query + " where guest_id = '%d'and check_in>'%s' and " \
#                         "check_out <'%s'" % (guest_id, from_date, to_date)
#     elif guest_id and from_date:
#         query = query + " where guest_id = '%d' and check_in>'%s'" % (
#             guest_id, from_date)
#     elif guest_id and to_date:
#         query = query + " where guest_id = '%d' and check_out<'%s'" % (
#             guest_id, to_date)
#     elif from_date and to_date:
#         query = query + " where check_in >'%s' and check_out<'%s'" % (
#             from_date, to_date)
#     elif from_date:
#         query = query + " where check_in>'%s'" % (from_date)
#     elif to_date:
#         query = query + " where check_out<'%s'" % (to_date)
#     elif guest_id:
#         query = query + " where guest_id ='%d'" % (guest_id)
#     self.env.cr.execute(query)
#     result = self.env.cr.dictfetchall()
#     print(result)
#     data = {
#         'id': self.id,
#         'model': self._name,
#         'start_date': self.from_date,
#         'end_date': self.to_date,
#         'today_date':self.today_date,
#         'guest_id': self.guest_id.name,
#         'table_data': result,
#         'form': self.read()[0],
#     }
#     print(data)
#     return {
#         'type': 'ir.actions.report',
#         'data': {'model': 'hotel.generate.report.wizard',
#                  'options': json.dumps(data,
#                                        default=date_utils.json_default),
#                  'output_format': 'xlsx',
#                  'report_name': 'Excel Report',
#                  },
#         'report_type': 'xlsx',
#     }
#
# def get_xlsx_report(self, data, response):
#
#     output = io.BytesIO()
#     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#     user_obj = self.env.user
#     sheet = workbook.add_worksheet('Hotel Accomodation Report')
#     heading = workbook.add_format(
#         {'font_size': 20, 'align': 'center', 'bold': True,
#          'bg_color': '#D3D3D3','border': 1})
#     format1 = workbook.add_format(
#         {'font_size': 10, 'align': 'left'})
# heading = workbook.add_format(
#     {'font_size': 20, 'align': 'center', 'bold': True,
#      'bg_color': '#D3D3D3','border': 1})
# format1 = workbook.add_format(
#     {'font_size': 10, 'align': 'left'})
# format2 = workbook.add_format(
#     {'font_size': 10, 'align': 'left', 'bold': True,
#      'bg_color': '#D3D3D3','border': 1})
#
#
# sheet.set_column(0, 9, 20)
# sheet.write('B2', user_obj.company_id.name, format1)
# sheet.write('B3', user_obj.company_id.street, format1)
# sheet.write('B4', user_obj.company_id.city, format1)
# sheet.write('B5', user_obj.company_id.zip, format1)
# sheet.write('B6', user_obj.company_id.state_id.name, format1)
# sheet.write('B7', user_obj.company_id.country_id.name, format1)
# sheet.merge_range('B8:G9', "Accomodation Report", heading)
#
# if data['start_date']:
#     sheet.write('B12', "Date From:", format2)
#     sheet.write('C12', data['start_date'], format1)
# if data['end_date']:
#     sheet.write('B13', "Date To:", format2)
#     sheet.write('C13', data['end_date'], format1)
# if data['guest_id']:
#     sheet.write('B14', 'Guest:', format2)
#     sheet.write('C14', data['guest_id'], format1)
# if not data['start_date'] & data['end_date']:
#     sheet.write('B13', "Date:", format2)
#     sheet.write('C13', data['today_date'], format1)
#
# row = 15
# col = 1
# sheet.write(row, col, 'Sl No.', format2)
# col += 1
# sheet.write(row, col, 'Reference', format2)
# col += 1
# sheet.write(row, col, 'Room No', format2)
# col += 1
# sheet.write(row, col, 'Check In', format2)
# col += 1
# sheet.write(row, col, 'Check Out', format2)
# col += 1
# if not data['guest_id']:
#     sheet.write(row, col, 'Guest', format2)
# col += 1
# row_number = 16
# i = 0
# for val in data['table_data']:
#     column_number = 1
#     i += 1
#     sheet.write(row_number, column_number, i,
#                 format1)
#     column_number += 1
#     sheet.write(row_number, column_number, val['accomodation_id'],
#                 format1)
#     column_number += 1
#     sheet.write(row_number, column_number, val['room_no'], format1)
#     column_number += 1
#     sheet.write(row_number, column_number, val['check_in'], format1)
#     column_number += 1
#     sheet.write(row_number, column_number, val['check_out'], format1)
#     column_number += 1
