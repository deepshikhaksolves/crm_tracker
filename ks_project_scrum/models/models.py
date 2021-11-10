# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class KsProjectScrumRelease(models.Model):
    _inherit = 'project.scrum.release'

    sprint_release_tasks_count = fields.Integer("Tasks", compute='get_sprint_release_tasks_count')

    def ks_sprint_release_tasks(self):
        print(self)
        return {
            'name': _('Scrum Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form,calendar,pivot,graph,activity',
            'domain': [('release_id','=',self.id)],
        }

    def get_sprint_release_tasks_count(self):
        count = self.env['project.task'].search_count([('release_id','=',self.id)])
        self.sprint_release_tasks_count = count


class KsProjectScrumSprint(models.Model):

    _inherit = 'project.scrum.sprint'

    sprint_tasks_count = fields.Integer("Tasks", compute='get_sprint_tasks_count')

    def ks_sprint_tasks(self):
        return {
            'name': _('Scrum Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form,calendar,pivot,graph,activity',
            'domain': [('sprint_id','=',self.id)],
        }

    def get_sprint_tasks_count(self):
        count = self.env['project.task'].search_count([('sprint_id','=',self.id)])
        self.sprint_tasks_count = count


