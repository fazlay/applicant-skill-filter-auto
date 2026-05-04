{
    'name': 'Custom Invoice Calculation',
    'version': '18.0.2.0.0',
    'summary': 'Allow custom Python calculation logic on invoice lines via product template',
    'depends': ['account', 'product'],
    'data': [
        'data/charge_product.xml',
        'report/report_invoice.xml',
        'views/product_template_views.xml',
        'views/account_move_line_views.xml',
        'views/account_move_views.xml',
        'views/accout_move_line.xml'
    ],
    'installable': True,
    'auto_install': False,
}
