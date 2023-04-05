# -*- coding: utf-8 -*-

from odoo import fields, models


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offers for real state properties"

    price = fields.Float(help="Price offered for the property.")
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False,
        help="Status of the offer for the property.",
    )
    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        required=True,
        help="Partners doing an offer for the property.",
    )
    property_id = fields.Many2one(
        'estate.property',
        string="Property",
        required=True,
        help="Real estate properties being offered.",
    )
