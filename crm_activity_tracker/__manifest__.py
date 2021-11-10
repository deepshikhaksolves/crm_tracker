# -*- coding: utf-8 -*-
{
    'name': "CRM Activity tracker",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ksolves India Ltd.",
    'sequence': 1,
    'website': "https://www.ksolves.com/",
    'category': 'Uncategorized',
    'version': '14.0.1.0.0',
    'depends': ['base', 'hr', 'crm', 'mail', 'sales_team'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_group.xml',
        'views/crm_activity_summary.xml',
        'views/crm_escalation_matrix.xml',
        'data/ir_sequence.xml',
        'data/ir_cron_job.xml',
        'data/crm_mail_format.xml',
    ],
    'post_init_hook': 'post_install_hook',
}
