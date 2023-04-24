# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class Property(models.Model):
    _name = "estate.property"
    _description = "Real estate properties"

    name = fields.Char(
        string="Title",
        required=True,
        help="Name of the property (required).",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        default="new",
        copy=False,
    )
    description = fields.Text(help="Description in detail of the property.")
    postcode = fields.Char(help="Postal code of the property.")
    date_availability = fields.Date(
        string="Available From",
        default=lambda self: self._default_date_availability(),
        copy=False,
        help="The property is available starting this date.",
    )
    expected_price = fields.Float(
        required=True,
        help="Expected price for the selling of the property (required).",
    )
    selling_price = fields.Float(
        readonly=True,
        copy=False,
        help="Price at which the property is sold.",
    )
    bedrooms = fields.Integer(
        default=2,
        help="Integer number of bedrooms of the property.",
    )
    living_area = fields.Integer(
        string="Living Area (sqm)",
        help="Integer number of sqm of living area of the property.",
    )
    facades = fields.Integer(help="Integer number of facades of the property.")
    garage = fields.Boolean(help="Marked if the property has garage.")
    garden = fields.Boolean(help="Marked if the property has garden.")
    garden_area = fields.Integer(
        string="Garden Area (sqm)",
        help="Integer area in sqm of the garden area.",
    )
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        help="Orientation of the garden.",
    )

    property_type_id = fields.Many2one(
        "estate.property.type",
        help="Type of the property.",
    )
    buyer_id = fields.Many2one(
        "res.partner",
        copy=False,
        help="Buyer, related to a partner.",
    )
    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesman",
        default=lambda self: self.env.user,
        help="Salesperson, related to a user.",
    )
    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Tags",
        help="Tags describing the property.",
    )
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers",
        help="Offerings for the property.",
    )

    total_area = fields.Integer(
        compute="_compute_total_area",
        help="Total area of the property.",
    )
    best_price = fields.Float(
        string="Best Offer",
        compute="_compute_best_price",
        help="Best price offer.",
    )

    def _default_date_availability(self):
        return fields.Date.today() + relativedelta(months=3)

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            offered_prices = record.offer_ids.mapped("price")
            record.best_price = max(offered_prices, default=0.0)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def _check_availability(self, error_msg):
        """ Errors en error if the property is not available. Raises an
        UserError when the property is not available for sale, that is, if it
        is sold or canceled. Receives a single record in `self` and an error
        message.
        """
        self.ensure_one()
        if self.state in ["sold", "canceled"]:
            message = _("%s property: %s", self.state.capitalize(), error_msg)
            raise UserError(message)

    def _clear_offers(self):
        """ Change state of offers to "refused". Set the state of all offers
        to "refused". Receives a single record in `self`.
        """
        self.ensure_one()
        for offer in self.offer_ids:
            if offer.status != "refused":
                offer.status = "refused"

    def _set_offer(self, selling_price, buyer):
        """ Set selling_price and buyer. Once an offer has been accepted this
        set the selling price and buyer of the property. Receives a single
        record in `self`.
        """
        self.ensure_one()
        self._clear_offers()
        self.selling_price = selling_price
        self.buyer_id = buyer

    def action_mark_sold(self):
        """ Set a property as sold when an offer is accepted. If the property
        is canceled raises an error.
        """
        message = _("Property cannot be sold.")
        for record in self:
            record._check_availability(message)
            record.state = "sold"
        return True

    def action_mark_canceled(self):
        """ Set a property as canceled and clear selling_price and buyer
        fields. If the property is already sold raises an error.
        """
        message = _("Property cannot be canceled.")
        for record in self:
            record._check_availability(message)
            record._clear_offers()
            record._set_offer(0.0, "")
            record.state = "canceled"
        return True
