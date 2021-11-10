# -*- coding: utf-8 -*-

from odoo import api, fields, models


class KsResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lead_lost_mail_receiver = fields.Many2one(comodel_name='res.partner', string='Lead Lost Mail Receiver')

    def set_values(self):
        super(KsResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ks_crm.lead_lost_mail_receive',
                                                         int(self.lead_lost_mail_receiver.id))

    def get_values(self):
        res_value = super(KsResConfigSettings, self).get_values()
        res_value.update(
            lead_lost_mail_receiver=int(self.env['ir.config_parameter'].sudo().get_param(
                'ks_crm.lead_lost_mail_receive')),
        )
        return res_value