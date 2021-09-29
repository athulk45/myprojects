import base64
import xlrd
from odoo import models, fields, _
from odoo.exceptions import UserError
from re import findall as regex_findall
from re import split as regex_split


class ImportRecord(models.TransientModel):
    _name = "import.record"

    file = fields.Binary(string="File", attachment=False)
    today_date = fields.Date(default=fields.Date.today())

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
                            pdt = self.env['product.product'].search(
                                [('id', '=', row_values[1])], limit=1)
                            lot = self.env['stock.production.lot'].search(
                                [('product_id', '=', pdt.id),
                                        ('name', '=', row_values[2])], limit=1)
                            stk = self.env['stock.quant'].search([
                                ('product_id', '=', pdt.id)],
                                limit=1)
                            if pdt.tracking == "lot":
                                if lot:
                                    lot.write({
                                        'product_qty': row_values[4]
                                    })
                                    stk.write({
                                        'inventory_quantity': row_values[4]
                                    })

                                else:
                                    print("no existing lot")
                                    print(type(row_values[4]))
                                    lot_vals = {
                                        'product_id': pdt.id,
                                        'name': row_values[2],
                                        'product_qty': row_values[4],
                                        'company_id': self.env.company.id,
                                    }
                                    lot.create(lot_vals)
                                    print(lot_vals)
                                    nolot = self.env['stock.production.lot'].search(
                                        [('product_id', '=', pdt.id),
                                                ('name', '=', row_values[2])])
                                    print(nolot)
                                    print(stk.product_uom_id)
                                    stk_vals = {
                                        'lot_id': nolot.id,
                                        'location_id': stk.location_id.id,
                                        'product_id': pdt.id,
                                        'inventory_quantity': row_values[4],
                                        'reserved_quantity': row_values[4],
                                        'available_quantity': row_values[4],
                                        'company_id': self.env.company.id,
                                    }
                                    stk.create(stk_vals)
                                    # move_vals = {
                                    #     'company_id': self.env.company.id,
                                    #     'date': self.today_date,
                                    #     'location_dest_id': stk.location_id.id,
                                    #     'location_id': 2,
                                    #     'product_uom_qty': row_values[4],
                                    #     'qty_done': row_values[4],
                                    #     'product_uom_id': stk.product_uom_id
                                    # }
                                    # self.env['stock.move.line'].create(move_vals)
                                    print(stk_vals)
                            elif pdt.tracking == "serial":
                                if lot:
                                    raise UserError(
                                        _('The serial number already exist'))
                                else:
                                    seq = row_values[2]
                                    count = int(row_values[4])
                                    initial_num = regex_findall("\d+", seq)
                                    print(initial_num)
                                    if not initial_num:
                                        raise UserError(
                                            _('The serial number must contain'
                                              'at least one digit.'))
                                    num = initial_num[-1]
                                    print("num", num)
                                    padding = len(initial_num)
                                    print("padding", padding)
                                    splitted = regex_split(num, seq)
                                    print("splitted", splitted)
                                    prefix = num.join(splitted[:-1])
                                    print("prefix", prefix)
                                    num = int(num)
                                    print("num", num)
                                    lot_names = []
                                    for i in range(0, count):
                                        lot_names.append('%s%s' % (
                                            prefix,
                                            str(num + i).zfill(padding)
                                        ))
                                        lot_vals = {
                                            'product_id': pdt.id,
                                            'name': lot_names[i],
                                            'product_qty': 1,
                                            'company_id': self.env.company.id,
                                        }
                                        lot.create(lot_vals)
                                        noserial = self.env[
                                            'stock.production.lot'].search(
                                            [('product_id', '=', pdt.id),
                                                    ('name', '=',
                                                     lot_names[i])])
                                        stk_vals = {
                                            'lot_id': noserial.id,
                                            'location_id': stk.location_id.id,
                                            'product_id': pdt.id,
                                            'reserved_quantity': 1,
                                            'inventory_quantity': 1,
                                            'available_quantity': 1,
                                            'company_id': self.env.company.id,
                                        }
                                        stk.create(stk_vals)
                                        print(lot_vals)

                            else:
                                print("false")
                                raise UserError(_('set tracking for products'))
            except IndexError:
                pass

