# -*- coding: utf-8 -*-

from odoo import fields, models


class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Tags for real estate properties"
    _sql_constraints = [
        ("unique_tag", "UNIQUE(name)", "Another tag with the same name already exist."),
    ]

    name = fields.Char(string="Tag", required=True, help="Tags for properties.")
