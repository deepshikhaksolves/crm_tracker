from odoo import fields, models, api
from odoo.exceptions import UserError


class CrmTiming(models.Model):
    _name = 'crm.timing'
    _description = 'Crm official timings'

    name = fields.Char(string='Name', required=True, default='Office Timing')
    login_time = fields.Float(string='Login Time', required=True, digits=(2, 2))
    logout_time = fields.Float(string='Logout Time', required=True, digits=(2, 2))

    @api.onchange('login_time', 'logout_time')
    def onchange_login_time(self):
        if self.login_time:
            login_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.login_time) * 60, 60)).split(':')
            login_time_hour = login_time[0]
            login_time_minute = login_time[1]
            if login_time_hour < '00' or login_time_hour > '24':
                raise UserError('Login Time Hour can only be between 00 to 24')
            if login_time_minute < '00' or login_time_minute > '60':
                raise UserError('Login Time minute can only be between 00 to 60')
        if self.logout_time:
            logout_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.logout_time) * 60, 60)).split(':')
            logout_time_hour = logout_time[0]
            logout_time_minute = logout_time[1]
            if logout_time_hour < '00' or logout_time_hour > '24':
                raise UserError('Logout Time Hour can only be between 00 to 24')
            if logout_time_minute < '00' or logout_time_minute > '60':
                raise UserError('Logout Time minute can only be between 00 to 60')

    @api.model
    def create(self, vals):
        if 'login_time' in vals and 'logout_time' in vals and vals['login_time'] == vals['logout_time']:
            raise UserError('Login Time and Logout Time cannot be same')
        res = super(CrmTiming, self).create(vals)
        return res
