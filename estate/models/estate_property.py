# -*- coding: utf-8 -*-

from odoo import fields, models


class Property(models.Model):
    _name = "estate.property"
    _description = "Real Estate properties"

    name = fields.Char(
        required=True,
        help="Name of the property (required).")
    description = fields.Text(help="Description in detail of the property.")
    postcode = fields.Char(help="Postal code of the property.")
    date_availability = fields.Date(
        help="The property is available starting this date.")
    expected_price = fields.Float(
        required=True,
        help="Expected price for the selling of the property (required).")
    selling_price = fields.Float(
        help="Price at which the property is sold.")
    bedrooms = fields.Integer(
        help="Integer number of bedrooms of the property.")
    living_area = fields.Integer(
        help="Integer number of sqm of living area of the property.")
    facades = fields.Integer(help="Integer number of facades of the property.")
    garage = fields.Boolean(help="Marked if the property has garage.")
    garden = fields.Boolean(help="Marked if the property has garden.")
    garden_area = fields.Integer(help="Integer area in sq2 of the garden area.")
    garden_orientation = fields.Selection(
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        help="Orientation of the garden."
    )
