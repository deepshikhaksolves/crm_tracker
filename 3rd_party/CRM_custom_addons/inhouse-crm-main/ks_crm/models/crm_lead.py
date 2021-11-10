# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from  odoo.exceptions import UserError


class KsLead(models.Model):
    _inherit = "crm.lead"

    def _get_default_source(self):
        return self.env['ks.lead.source'].search([('name', '=', 'Twak')], limit=1)

    def _get_default_technology(self):
        return self.env['ks.lead.technology'].search([('name', '=', 'Odoo')], limit=1)

    partner_address_email = fields.Char(string='Partner Contact Email', related='partner_id.email')
    ks_technology_id = fields.Many2one(comodel_name='ks.lead.technology', string='Technology',
                                       default=lambda self: self._get_default_technology())
    ks_type_id = fields.Many2one(comodel_name='ks.lead.type', string='Type')
    ks_source_id = fields.Many2one(comodel_name='ks.lead.source',
                                   string='Source',
                                   default=lambda self: self._get_default_source())
    twak_user_id = fields.Many2one('res.users', string='Tawk Lead Generator', index=True, tracking=True, default=lambda self: self.env.user)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True, default=False)

    def unlink(self):
        if self.env.user.has_group('sales_team.group_sale_salesman'):
            raise UserError(_("You are not allowed to delete this record"))

    def get_access_link(self):
        """To get link of Lead/Opportunity."""
        return self._notify_get_action_link('view')
    
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        self = self.with_context(default_user_id=False)

        if custom_values is None:
            custom_values = {}
            
        defaults = {
            #'description': msg_dict.get('body'),
            'type': 'opportunity',
            'stage_id': self.env.ref('crm.stage_lead1').id,
            'ks_source_id': self.env.ref('ks_crm.ks_lead_source_email').id
        }
        
        custom_values.update(defaults)
        return super(KsLead, self).message_new(msg_dict, custom_values=defaults)
    
