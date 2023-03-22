# -*- coding: utf-8 -*-

from odoo import fields, models
from dateutil.relativedelta import relativedelta


class Property(models.Model):
    _name = "estate.property"
    _description = "Real Estate properties"

    name = fields.Char(
        string="Title",
        required=True,
        help="Name of the property (required).")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer", "Offer"),
            ("received", "Received"),
            ("accepted", "Accepted"),
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
        help="The property is available starting this date.")
    expected_price = fields.Float(
        required=True,
        help="Expected price for the selling of the property (required).")
    selling_price = fields.Float(
        readonly=True,
        copy=False,
        help="Price at which the property is sold.")
    bedrooms = fields.Integer(
        default=2,
        help="Integer number of bedrooms of the property.")
    living_area = fields.Integer(
        string="Living Area (sqm)",
        help="Integer number of sqm of living area of the property.")
    facades = fields.Integer(help="Integer number of facades of the property.")
    garage = fields.Boolean(help="Marked if the property has garage.")
    garden = fields.Boolean(help="Marked if the property has garden.")
    garden_area = fields.Integer(
        string="Garden Area (sqm)",
        help="Integer area in sqm of the garden area.")
    garden_orientation = fields.Selection(
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        help="Orientation of the garden."
    )

    def _default_date_availability(self):
        return fields.Date.today() + relativedelta(months=3)
