# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Property Division',
    'version' : '1.1',
    'summary': 'Property',
    'sequence': 30,
    'description': """
Property Modules
====================
The specific and easy-to-use Property Sales system in Odoo 
    """,
    'category': 'Property',
    'website': ' ',
    #'images' : ['images/accounts.jpeg','images/bank_statement.jpeg','images/cash_register.jpeg','images/chart_of_accounts.jpeg','images/customer_invoice.jpeg','images/journal_entries.jpeg'],
    'depends' : ['base','account', 'sale', 'sale_stock', 'stock', 'purchase','sales_team'],
    'data': [
        
        'view/property_unit.xml',
        'view/reserved.xml',
        'view/booking.xml',
        'view/property_sale.xml',
        # 'view/nota_kredit.xml',
        'view/iom.xml',
        'view/installment.xml',
        'view/estate_ipl.xml',
        'view/budget.xml',
        'view/material_req.xml',
        'sequence/sequence.xml',
        'menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
