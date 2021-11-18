from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class ErpEscalationMatrix(models.Model):
    _name = 'erp.escalation.matrix'
    _description = "It holds the information for the Managers Hierarchy"
    # _rec_name = 'escalation_matrix_number'

    escalation_matrix_number = fields.Char("Escalation Matrix", default="New")
    manager_id = fields.Many2one('hr.employee', string='Lead Manager')
    type_of_matrix = fields.Selection([
        ('services', 'Services'),
        ('products', 'Products')], 'Matrix Type')
    managers_ids = fields.One2many(
        'escalation.matrix.hr.employee', 'escalation_matrix_id')
    name = fields.Char(string='Name')

    def name_get(self):
        result = []
        for matrix in self:
            name = matrix.escalation_matrix_number + ' ' + matrix.name
            result.append((matrix.id, name))
        return result

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('escalation_matrix_number', _('New')) == _('New'):
            vals['escalation_matrix_number'] = self.env['ir.sequence'].next_by_code(
                'erp.escalation.matrix') or _('New')

        return super(ErpEscalationMatrix, self).create(vals)

    def write(self, vals):
        if 'managers_ids' in vals:
            activity_type_ids = self.env['mail.activity.type'].search([('escalation_matrix_id', '=', self.id)])
            for type_id in activity_type_ids:
                type_id.write({
                    'next_sequence': len(vals.get('managers_ids')),
                })
        return super(ErpEscalationMatrix, self).write(vals)


class ErpEscalationEmployee(models.Model):
    _name = "escalation.matrix.hr.employee"

    sequence = fields.Integer("Sequence")
    serial_no = fields.Integer("Hierarchy Order", compute='compute_serial_no')
    escalation_matrix_id = fields.Many2one('erp.escalation.matrix')
    salesperson_id = fields.Many2one('hr.employee', string='Manager')
    salesperson_manager = fields.Many2one('hr.employee', related='salesperson_id.parent_id', string="Parent "
                                                                                                    "Manager")
    work_email = fields.Char('Email', related='salesperson_id.work_email')

    def compute_serial_no(self):
        for rec in self:
            rec.serial_no = rec.sequence * 10



class ErpEscalationCrm(models.Model):
    _inherit = 'crm.lead'

    type_of_matrix = fields.Selection([
        ('services', 'Services'),
        ('products', 'Products')], 'Matrix Type')
    next_activity_sequence = fields.Integer('Next Activity Sequence')
    activity_sequence_flag = fields.Boolean(string="Activity Flag")

    @api.model_create_multi
    def create(self, vals_list):

        # activity_type = None
        # if vals_list and 'user_id' in vals_list[0]:
        #     activity_type = self.env['mail.activity.type'].search([]).sorted(key=lambda e: e.sequence)
        #     if len(activity_type) > 1:
        #         vals_list[0].update({'next_activity_sequence': activity_type.sequence})

        res_id = super(ErpEscalationCrm, self).create(vals_list)

        if vals_list and 'user_id' in vals_list[0] and 'team_id' in vals_list[0]:
            # creating the schedule activity according the activity summary
            sale_id = self.env['crm.team'].browse(vals_list[0].get('team_id'))
            for activity in sale_id.activity_id:
                self.env['mail.activity'].create({
                    # 'summary': activity_summary[0].activity_summary,
                    # 'date_deadline': date.today() + relativedelta(days=activity_summary[0].due_date_days),
                    'activity_type_id': activity.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id,
                    'res_id': res_id.id,
                    'user_id': res_id.user_id.id,
                    # 'next_activity_sequence': activity_summary[1].sequence if len(activity_summary) > 1 else 0,
                    'is_erp_activity': True,
                    'is_crm_lead': True,
                    'next_mail_manager_sequence': activity.next_sequence,
                })
        return res_id

    def write(self, vals):

        # if changing the salesperson and any activity is created
        # if 'user_id' in vals and self.activity_ids and self.activity_ids.is_erp_activity:
        #     self.activity_ids.user_id = vals['user_id']

        if 'user_id' in vals and not self.activity_ids:
            # activity_summary = self.env['erp.crm.activity.summary'].search([]).sorted(key=lambda e: e.sequence)
            # if len(activity_summary) > 1:
            #     vals.update({'next_activity_sequence': activity_summary[1].sequence})
            sale_id = self.env['crm.team'].browse(vals.get('team_id'))
            for activity in sale_id.activity_id:
                self.env['mail.activity'].create({
                    'activity_type_id': activity.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id,
                    'res_id': self.id,
                    'user_id': self.user_id.id or vals['user_id'],
                    'is_erp_activity': True,
                    'is_crm_lead': True,
                    'mail_reminder_day': activity.delay_count,
                    'next_mail_manager_sequence': activity.next_sequence,
                })
        elif 'user_id' in vals or 'team_id'  in vals:
            if 'user_id' in vals:
                auto_activity_ids = [i.id for i in self.team_id.activity_id]
                for activity in self.activity_ids:
                    if activity.activity_type_id.id in auto_activity_ids:
                        auto_activity_ids.remove(activity.activity_type_id.id)
                        activity.write({
                            'user_id': vals.get('user_id')
                        })
                if len(auto_activity_ids) > 0:
                    for activity_id in auto_activity_ids:
                        activity = self.env['mail.activity.type'].browse(
                            activity_id)
                        self.env['mail.activity'].create({
                            'activity_type_id': activity.id,
                            'res_model_id': self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id,
                            'res_id': self.id,
                            'user_id': vals['user_id'],
                            'is_erp_activity': True,
                            'is_crm_lead': True,
                            'mail_reminder_day': activity.delay_count,
                            'next_mail_manager_sequence': activity.next_sequence,
                        })
            else:
                sale_id = self.env['crm.team'].browse(vals.get('team_id'))
                for activity in sale_id.activity_id:
                    self.env['mail.activity'].create({
                        'activity_type_id': activity.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id,
                        'res_id': self.id,
                        'user_id': self.user_id.id or vals['user_id'],
                        'is_erp_activity': True,
                        'is_crm_lead': True,
                        'mail_reminder_day': activity.delay_count,
                        'next_mail_manager_sequence': activity.next_sequence,
                    })


        return super(ErpEscalationCrm, self).write(vals)


class ErpScheduleActivity(models.Model):
    _inherit = 'mail.activity'

    next_activity_sequence = fields.Integer('Next Activity Sequence')
    mail_reminder_day = fields.Integer('Mail Reminder Day', default=2)
    is_erp_activity = fields.Boolean('Erp Activity')
    next_mail_due_date = fields.Date(
        string='Next mail Remainder Date', compute='compute_next_mail_due_date')
    is_crm_lead = fields.Boolean(
        "Is Crm Lead")
    is_mail_triggered = fields.Boolean("Mail Triggered")
    next_mail_manager_sequence = fields.Integer("Next Manager Mail Sequence")

    @api.onchange('mail_reminder_day', 'date_deadline')
    def compute_next_mail_due_date(self):
        for rec in self:
            if rec.res_model == 'crm.lead' and rec.date_deadline:
                rec.is_crm_lead = True
                rec.next_mail_due_date = rec.date_deadline + \
                    relativedelta(days=rec.mail_reminder_day)

    # def _action_done(self, feedback=False, attachment_ids=None):
    #     if self.res_model == 'crm.lead':
    #         crm_id = self.env['crm.lead'].browse(self.res_id)
    #         if self.next_activity_sequence:
    #             activity_summary = self.env['erp.crm.activity.summary'].search([]).sorted(key=lambda e: e.sequence)
    #             upcoming_summary = activity_summary.filtered(
    #                 lambda summary: summary.sequence >= self.next_activity_sequence
    #             )
    #             # creating the schedule activity according the activity summary
    #             if upcoming_summary:
    #                 self.env['mail.activity'].create({
    #                     'summary': upcoming_summary[0].activity_summary,
    #                     'date_deadline': date.today() + relativedelta(days=upcoming_summary[0].due_date_days),
    #                     'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
    #                     'res_model_id': self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1).id,
    #                     'res_id': self.res_id,
    #                     'user_id': self.user_id.id,
    #                     'next_activity_sequence': upcoming_summary[1].sequence if len(upcoming_summary) > 1 else 0,
    #                     'is_erp_activity': True,
    #                     'is_crm_lead': True
    #                 })
    #                 if len(upcoming_summary) > 1:
    #                     crm_id.write({
    #                         'next_activity_sequence': upcoming_summary[1].sequence,
    #                     })
    #         else:
    #             crm_id.write({
    #                 'next_activity_sequence': 0,
    #                 'activity_sequence_flag': True
    #             })

    #     return super(ErpScheduleActivity, self)._action_done(feedback=feedback, attachment_ids=attachment_ids)

    def action_feedback_schedule_next(self, feedback=False):
        model = self.res_model
        is_erp_activity = self.is_erp_activity

        action = super(ErpScheduleActivity, self).action_feedback_schedule_next(
            feedback=feedback)

        # don't open the window in case of schedule next activity
        if model == 'crm.lead' and is_erp_activity and action:
            action = False
        return action

    def crm_send_email(self):
        crm_mail_template_id = self.env.ref(
            'crm_activity_tracker.mail_crm_schedule_activity')
        if crm_mail_template_id:
            activities = self.env['mail.activity'].search(
                [('is_erp_activity', '=', True), ('res_model', '=', 'crm.lead'),
                 ('next_mail_due_date', '=', fields.Datetime.to_string((date.today())))])
            user_id = None
            for rec in activities:
                values = crm_mail_template_id.generate_email(rec.id, ['subject', 'body_html', 'email_from', 'email_to',
                                                                      'partner_to', 'email_cc', 'reply_to',
                                                                      'scheduled_date'])
                crm_obj = rec.env['crm.lead'].browse(rec.res_id)
                escalation_matrix = rec.activity_type_id.escalation_matrix_id

                if escalation_matrix:
                    if not rec.is_mail_triggered:
                        salespersons_ids = escalation_matrix.managers_ids.sorted(
                            'serial_no', reverse=True)
                        if salespersons_ids:
                            user_id = salespersons_ids[0].salesperson_id
                            values['email_to'] = user_id.work_email
                            if len(salespersons_ids) > 1:
                                rec.next_mail_manager_sequence = salespersons_ids[1].serial_no
                        else:
                            _logger.error(
                                "No Salesperson is defined in escalation matrix" + str(crm_obj.type_of_matrix))
                    else:
                        manager_ids = escalation_matrix.managers_ids.filtered(
                            lambda manager_id: manager_id.serial_no >= rec.next_mail_manager_sequence)
                        if manager_ids:
                            emails = set(
                                manger_id.work_email for manger_id in manager_ids)
                            values['email_to'] = ','.join(emails)
                            next_sequence_manager_ids = escalation_matrix.managers_ids.filtered(
                                lambda manager_id: manager_id.serial_no < rec.next_mail_manager_sequence)
                            sorted_manager = next_sequence_manager_ids.sorted(
                                'serial_no', reverse=True)
                            if sorted_manager:
                                rec.next_mail_manager_sequence = sorted_manager[0].serial_no

                else:
                    _logger.error(
                        "No escalation matrix is defined for " + str(crm_obj.type_of_matrix))

                values['email_from'] = "odoobot@example.com"
                values['body_html'] = values['body_html']
                mail = self.env['mail.mail'].create(values)
                mail.send()
                if not rec.is_mail_triggered:
                    rec.is_mail_triggered = True


class ErpActivityType(models.Model):
    _inherit = 'mail.activity.type'

    escalation_matrix_id = fields.Many2one(
        'erp.escalation.matrix', string="Escalation Matrix")
    model = fields.Char('Model', related='res_model_id.model')
    is_erp_activity = fields.Boolean('Is Erp activity')
    next_sequence = fields.Integer(string='Next Sequence')

    @api.onchange('escalation_matrix_id')
    def _onchange_escalation_matrix_id(self):
        for rec in self:
            if rec.escalation_matrix_id: 
                rec.next_sequence = len(rec.escalation_matrix_id.managers_ids) if rec.escalation_matrix_id.managers_ids else 0

class ErpCrmTeam(models.Model):
    _inherit = 'crm.team'

    activity_id = fields.Many2many(
        'mail.activity.type', string='Activity', domain="[('is_erp_activity', '=', True)]")
