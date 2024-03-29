# -*- coding: utf-8 -*-

{
    'name': 'Real Estate',
    'author': 'Vauxoo',
    'version': '16.0.1.0.0',
    'license': 'OPL-1',
    'category': 'Real Estate/Brokerage',
    'depends': ['base'],
    'data': [
        'security/estate_groups.xml',
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',
        'data/estate.property.type.csv',
        'demo/estate_property.xml',
        'demo/estate_property_offer.xml',
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml',
    ],
    'application': True,
}
