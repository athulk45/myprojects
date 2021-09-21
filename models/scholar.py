from odoo import fields, models, api


class ResearchScholar(models.Model):
    _name = "research.scholar"
    _description = "scholar"
    _rec_name = "f_name"

    unique_id = fields.Integer(string="Scholar Id")
    _sql_constraints = [('field_unique', 'unique(scholar_id)',
                         'Choose another value for Scholar Id - it has to be '
                         'unique!')]
    f_name = fields.Char(string="First Name", required=True)
    m_name = fields.Char(string="Middle Name")
    l_name = fields.Char(string="Last Name", required=True)
    age = fields.Integer(string='Age')
    sex = fields.Selection([('male', 'Male'), ('female', 'Female')])

    institute_id = fields.Many2one(string="Name",
                                   comodel_name="research.institute")
    i_address = fields.Text(string="Address", related="institute_id.address")
    i_email = fields.Char(string="Email", related="institute_id.email")
    i_phone = fields.Char(string="Phone", related="institute_id.phone")

    partner_id = fields.Many2one('res.partner', string="Related Partner")
    scholar_id = fields.Char(string='Serial Number', required=True, copy=False,
                             readonly=True, default=lambda self: 'New')

    @api.model
    def create(self, val):
        print(val)
        if val.get('scholar_id', 'New' == 'New'):
            val['scholar_id'] = self.env['ir.sequence'].next_by_code(
                'research.scholar')
            return super(ResearchScholar, self).create(val)


class Contacts(models.Model):
    _inherit = "res.partner"
    scholar = fields.Boolean(default=False)
    count = fields.Integer(compute='scholar_count')

    def scholar_count(self):
        for rec in self:
            scholar_count = rec.env['research.scholar']. \
                search_count([('partner_id', '=', rec.id)])
            rec.count = scholar_count

    def get_scholar(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'scholar',
            'view_mode': 'tree,form',
            'res_model': 'research.scholar',
            'domain': [('partner_id', '=', self.id)],
            'target': 'current',
        }
