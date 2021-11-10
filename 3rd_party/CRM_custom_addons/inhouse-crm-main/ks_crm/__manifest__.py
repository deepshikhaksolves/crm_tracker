# -*- coding: utf-8 -*-
{
    'name': 'Ksolves CRM',
    'summary': "Ksolves CRM, helps in keeping track of lead/opportunities.",
    'description': """
        This module has all the crm customization for Ksolves.
    """,
    'author': "Ksolves India Pvt. Ltd.",
    'website': 'https://www.ksolves.com/',
    'maintainer': 'Ksolves India Pvt. Ltd.',
    'version': '1.0.0',
    'category': 'Sales',
    'support': 'sales@ksolves.com',
    'sequence': 1,

    'depends': [
        'mail','crm'
    ],
    'data': [
        'data/mail_template_data.xml',
        'data/lead_data.xml',


        'security/ir.model.access.csv',

        'views/ks_lead_source_view.xml',
        'views/ks_lead_technology_view.xml',
        'views/ks_lead_type_view.xml',
        'views/crm_lead_view.xml',
        'views/res_config_settings_view.xml',

        'wizard/crm_lead_lost_view.xml',
    ],
    'qweb': [
        'static/src/xml/chatter.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
