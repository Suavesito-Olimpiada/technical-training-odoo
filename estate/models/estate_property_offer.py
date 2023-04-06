# -*- coding: utf-8 -*-

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


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
    validity = fields.Integer(
        string="Validity (days)",
        default=7,
        help="Valid days for the offer.",
    )

    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        help="Deadline for the offer.",
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today()

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - record.create_date.date()).days
