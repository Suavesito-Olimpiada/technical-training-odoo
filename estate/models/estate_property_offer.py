# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offers for real state properties"

    price = fields.Float(help="Price offered for the property.")
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
        help="Status of the offer for the property.",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
        help="Partners doing an offer for the property.",
    )
    property_id = fields.Many2one(
        "estate.property",
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
                record.date_deadline = fields.Date.today() + relativedelta(days=7)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - record.create_date.date()).days

    def action_accept(self):
        """ Set an offer as accepted and set the selling_price and buyer for
        the asociated property. If the property asociated with the offer is
        canceled or sold raises an error.
        """
        message = _("Property cannot accept offers.")
        for record in self:
            record.property_id._check_availability(message)
            record.property_id._set_offer(record.price, record.partner_id)
            record.status = "accepted"
        return True

    def action_refuse(self):
        """ Set an offer as refused and unset the selling_price and buyer for
        the asociated property in case necesary. If the property asociated with
        the offer is canceled or sold raises an error.
        """
        message = _("Property cannot refuse offers.")
        for record in self:
            record.property_id._check_availability(message)
            if record.status == "accepted":
                record.property_id._set_offer(0.0, "")
            record.status = "refused"
        return True
