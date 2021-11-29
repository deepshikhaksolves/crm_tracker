from odoo import models, fields, api, _
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
_logger = logging.getLogger(__name__)


class CrmLeadInherit(models.Model):
    _inherit = "crm.lead"

    @api.model
    def create(self, vals):
        res = super(CrmLeadInherit, self).create(vals)
        if not res.user_id:
            model_id = self.env['ir.model'].search([('model', '=', 'crm.lead')], limit=1)
            activity_type_id = self.env['mail.activity.type'].search([('assignment_reminder', '=', True),
                                                                      ('escalation_matrix_id', '=', False),
                                                                      ('type_of_matrix', '=', False)], limit=1)
            date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type_id)
            date_deadline = datetime.strptime(date_deadline, '%Y-%m-%d %H:%M:%S')
            activity_id = self.env['mail.activity'].create({
                'res_model': 'crm.lead',
                'res_id': res.id,
                'res_model_id': model_id.id,
                'activity_type_id': activity_type_id.id,
                'date_deadline': date_deadline,
                'is_erp_activity': True,
                'is_lead_assignment': True,
                'summary': activity_type_id.name,
                'user_id': activity_type_id.responsible_person_id.id,
            })
            self.get_datedeadline_from_timing(activity_id, activity_type_id)
        return res

    def get_datedeadline_from_timing(self, activity_id, activity_type_id):
        timing = self.env['crm.timing'].search([], limit=1)
        if timing:
            now_time = datetime.utcnow().replace(second=00, microsecond=00)
            login_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(timing.login_time) * 60, 60)).split(':')
            logout_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(timing.logout_time) * 60, 60)).split(':')
            login_time = datetime.now().replace(hour=int(login_time[0]), minute=int(login_time[1]), second=00,
                                                microsecond=0)
            logout_time = datetime.now().replace(hour=int(logout_time[0]), minute=int(logout_time[1]), second=00,
                                                 microsecond=0)
            local_timezone = pytz.timezone(self.env.user.tz)
            naive_login = datetime.strptime(str(login_time), "%Y-%m-%d %H:%M:%S")
            naive_logout = datetime.strptime(str(logout_time), "%Y-%m-%d %H:%M:%S")
            local_login = local_timezone.localize(naive_login, is_dst=None)
            local_logout = local_timezone.localize(naive_logout, is_dst=None)
            login_utc = local_login.astimezone(pytz.utc).replace(tzinfo=None)
            logout_utc = local_logout.astimezone(pytz.utc).replace(tzinfo=None)
            if now_time < login_utc:
                diff = login_utc - now_time
                activity_id.date_deadline = activity_id.date_deadline + timedelta(seconds=diff.seconds)
            elif now_time > logout_utc - timedelta(hours=1):
                base = (now_time + timedelta(days=1)).replace(hour=login_utc.hour, minute=login_utc.minute)
                base += relativedelta(**{activity_type_id.delay_unit: activity_type_id.delay_count})
                activity_id.date_deadline = datetime.strftime(base, "%Y-%m-%d %H:%M:%S")
