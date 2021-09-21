
{
    'name' : 'Research Management',
    'version' : '14.0.1.0',
    'summary':'Research management software',
    'sequence':-10,
    'description': """""",
    'category': 'Sales',
    'website': 'https://www.odoo.com/page/billing',
    'images' : ['images/accounts.jpeg','images/bank_statement.jpeg',
                'images/cash_register.jpeg',
                'images/chart_of_accounts.jpeg',
                'images/customer_invoice.jpeg','images/journal_entries.jpeg'],
    'depends' : ['contacts','sale','account'],
    'data': ['security/ir.model.access.csv',
             'data/data.xml',
             'security/scholar_security.xml',
             'views/scholar_view.xml',
             'views/book_view.xml',
             ],
    'demo': [],
    'installable': True,
    'application': True,
    #'post_init_hook': '_account_post_init',
    'license': 'LGPL-3',
}