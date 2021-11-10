# -*- coding: utf-8 -*-

from . import models
from odoo.api import Environment, SUPERUSER_ID


def post_install_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    user_data = {"users": [(4, user_id.id) for user_id in (env['res.users'].search([])) if
                              user_id.has_group('base.group_system')]}
    crm_due_days_manager = env.ref('crm_activity_tracker.crm_due_days_manager')
    crm_due_days_manager.write(user_data)
