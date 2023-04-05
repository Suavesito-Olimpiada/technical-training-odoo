# -*- coding: utf-8 -*-

from odoo import fields, models


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real estate property type"

    name = fields.Char(
        string="Property Type",
        required=True,
        help="Type of the property (required).",
    )
