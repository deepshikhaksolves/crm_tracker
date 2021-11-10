# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class KsCrmLeadLost(models.TransientModel):
    _inherit = "crm.lead.lost"


    def action_lost_reason_apply(self):
        res = super(KsCrmLeadLost, self).action_lost_reason_apply()
        self.send_lead_lost_mail()
        return res

    def get_partner(self):
        """For getting the default partner from settings."""
        partner_id_from_setting = int(self.env['ir.config_parameter'].sudo().get_param(
                'ks_crm.lead_lost_mail_receive')) or False
        partner_from_setting = self.env['res.partner'].browse(partner_id_from_setting)
        return partner_from_setting

    def send_lead_lost_mail(self):
        """For send email when a lead is lost."""
        # To find all the leads fo which lost reason is updated.
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        for each_lead in leads:
            partner_from_setting = self.get_partner()
            if partner_from_setting:
                subject = """Lead/Opportunity [{lead_code}-{opp_name}] is lost.""".format(lead_code=each_lead.code,
                                                                                          opp_name=each_lead.name)
                email_list = [follower.email for follower in each_lead.message_follower_ids.mapped('partner_id') if
                              follower.id != each_lead.user_id.partner_id.id and follower.email]
                ks_email_cc = ",".join(email_list)
                template_id = self.env.ref('ks_crm.ks_lost_lead_mail_template')
                values = template_id.generate_email(each_lead.id,['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
                values['email_to'] = partner_from_setting.email
                values['email_cc'] = ks_email_cc
                values['email_from'] = self.env.user.email_formatted
                values['body_html'] = values['body_html']
                values['subject'] = subject
                mail = self.env['mail.mail'].create(values)
                try:
                    mail.send()
                except Exception as e:
                    _logger.exception("Exception %s during sending the lost lead reason mail." % str(e))
            else:
                raise UserError(_(
                    "You can't mark a lead/opportunity as lost. As 'Lead Lost Mail Receiver' field in settings, "
                    "is empty."))

