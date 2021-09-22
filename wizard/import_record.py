import base64
import xlrd
from odoo import models, fields
from odoo.exceptions import UserError


class ImportRecord(models.TransientModel):
    _name = "import.record"

    file = fields.Binary(string="File", attachment=False)
    prodt_id = fields.Many2one('stock.move.line')

    def import_lot(self):
        try:
            xl = xlrd.open_workbook(
                file_contents=base64.decodestring(self.file))
            print("test")
        # except FileNotFoundError:
        #     raise UserError(
        #         'No such file or directory found. \n%s.' % self.file)
        except xlrd.biffh.XLRDError:
            raise UserError('Only excel files are supported')
        for rec in xl.sheets():
            print("loop")
            try:
                print(rec.name)
                if rec.name == 'Sheet1':
                    for row in range(rec.nrows):
                        print(row)
                        if row >= 1:
                            row_values = rec.row_values(row)
                            print(row_values)
                            # split = row_values[0].split('_')
                            # print(split)
                            pdt = self.env['product.product']\
                                .search([('id', '=', row_values[1])], limit=1)
                            print(pdt)
                            if pdt.tracking == "serial":
                                print("serial")

                            elif pdt.tracking == "lot":
                                print(pdt.tracking)
                                print(row_values[2])
                            lot = self.env['stock.move.line']. \
                                search([('move_line_nosuggest_ids.lot_name', '=', row_values[2])],
                                       limit=1)
                            print(lot)
                            if lot:
                                print("exist")
                            else:
                                print("false")


                            #print(product_vals)

            except IndexError:
                pass



