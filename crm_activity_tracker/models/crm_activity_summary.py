from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ErpCrmActivitySummary(models.Model):
    _name = "erp.crm.activity.summary"
    _description = "It hold the information of Activity Summary"
    _rec_name = 'activity_summary'
    _order = 'sequence,id'

    activity_summary = fields.Char('Activities')
    due_date_days = fields.Integer('Due Date(days)')
    sequence = fields.Integer("Sequence")

    @api.model_create_multi
    def create(self, vals):
        rec = self.env["erp.crm.activity.summary"].search([]).sorted(lambda x: x.sequence, reverse=True)
        if rec:
            next_seq = rec[0].sequence + 1
            vals[0].update({
                'sequence': next_seq
            })
        return super(ErpCrmActivitySummary, self).create(vals)