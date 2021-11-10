# -*- coding: utf-8 -*-

from odoo import fields, models


class KsLeadTechnology(models.Model):
    _name = "ks.lead.technology"
    _description = "Lead Technology"

    name = fields.Char(string="Name")
