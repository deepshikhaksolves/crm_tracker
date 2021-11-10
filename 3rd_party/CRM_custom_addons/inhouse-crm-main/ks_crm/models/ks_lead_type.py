# -*- coding: utf-8 -*-

from odoo import fields, models


class KsLeadType(models.Model):
    _name = "ks.lead.type"
    _description = "Lead Type"

    name = fields.Char(string="Name")