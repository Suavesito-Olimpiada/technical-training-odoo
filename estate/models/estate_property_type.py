# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real estate property type"
    _order = "sequence, name"
    _sql_constraints = [
        ("unique_type", "UNIQUE(name)", "Another type with the same name already exist."),
    ]

    name = fields.Char(
        string="Property Type",
        required=True,
        help="Type of the property (required).",
    )
    property_ids = fields.One2many(
        "estate.property",
        "property_type_id",
        string="Properties",
        help="List of properties for every type.",
    )
    sequence = fields.Integer(default=1, help="Used to order types of properties.")
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_type_id",
        string="Offers",
        help="Offers for some type of property.",
    )

    offer_count = fields.Integer(
        compute="_compute_offer_count",
        help="Number of offer for a type of property.",
    )

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
