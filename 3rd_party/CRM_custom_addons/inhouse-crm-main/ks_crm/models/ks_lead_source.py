# -*- coding: utf-8 -*-

from odoo import fields, models


class KsLeadSource(models.Model):
    _name = "ks.lead.source"
    _description = "Lead Source"

    name = fields.Char(string="Name")
