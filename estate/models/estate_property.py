# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class Property(models.Model):
    _name = "estate.property"
    _description = "Real estate properties"
    _order = "id DESC"
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "The expected price must be strictly positive."),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The selling price must be positive."),
    ]

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

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company.id,
        help="Company managing the property."
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

    def _check_availability(self, error_msg=False):
        """ Errors if the property is not available. Raises an UserError when
        the property is not available for sale, that is, if it is sold or
        canceled. Receives a single record in `self` and an error message.
        """
        self.ensure_one()
        error_msg = error_msg or _("Cannot complete the action.")
        if self.state in ["sold", "canceled"]:
            message = _("%s property: %s", self.state.capitalize(), error_msg)
            raise UserError(message)

    def _check_accepted_offer(self):
        """ Verify that there is one accepted offer and raises an error in case
        there is not. Receives a single record in `self`.
        """
        self.ensure_one()
        message = _("Cannot sell a property without an accepted offer.")
        if self.state != "offer_accepted":
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

    def _check_new_offer_price(self, price):
        """ Check the price of a new offer. When a new offer is crated it must
        be greater then all previous offers to be valid. Receives a single
        record in `self`.
        """
        self.ensure_one()
        max_offer_price = max(self.offer_ids.mapped("price"), default=0.0)
        message = _("The offer must be greater than %.2f.", max_offer_price)
        if float_compare(max_offer_price, price, precision_digits=2) == 1:
            raise UserError(message)

    def action_mark_sold(self):
        """ Set a property as sold when an offer is accepted. If the property
        is canceled, or does not have an accepted offer, raises an error.
        """
        message_availability = _("Property cannot be sold.")
        for record in self:
            record._check_accepted_offer()
            record._check_availability(message_availability)
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

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        """ Check that the `selling_price` of a property is greater or equal
        than 90% of the `expected_price`. The selling price is originally 0.0
        so only after changing it to something strictly greater than 0.0 is the
        verification done, for this to work as expected is necessary to use the
        `>` operator of python intead of the recomended `float_is_zero`.
        """
        for record in self:
            if record.selling_price > 0.0:
                minimum_price = record.expected_price * 0.9
                if float_compare(record.selling_price, minimum_price, precision_digits=2) == -1:
                    raise ValidationError(
                        _("The selling price cannot be lower than 90% of expected price.")
                    )

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        if any(record.state not in ("new", "canceled") for record in self):
            message = _("Cannot delete a property that is not new or canceled.")
            raise UserError(message)
