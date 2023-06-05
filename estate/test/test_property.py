# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import Form


@tagged('post_install', '-at_install')
class TestPropertyOffer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestPropertyOffer, cls).setUpClass()

        cls.partner = cls.env['res.partner'].create({
            'name': 'Pepe',
        })
        cls.properties = cls.env['estate.property'].create([{
            'name': 'property_1',
            'expected_price': 10000,
        }])
        cls.offers = cls.env['estate.property.offer'].create([{
            'partner_id': cls.partner.id,
            'property_id': cls.properties[0].id,
            'expected_price': 9000,
        }])

    def test_property_garden(self):
        """Test the garden related properties by default and doing `onchange`'s"""
        with Form(self.properties[0]) as prop:
            # default
            self.assertEqual(prop.garden_area == 0)
            self.assertIs(prop.garden_orientation, False)  # why Is intead of Equal?
            # `onchange`'ed
            prop.garden = True
            self.assertEqual(prop.garden_area, 10)
            self.assertEqual(prop.garden_orientation, "north")
            # `onchange`'ed
            prop.garden = False
            self.assertEqual(prop.garden_area == 0)
            self.assertIs(prop.garden_orientation, False)

    def test_action_sell(self):
        """Test that `action_sold` behaves as it should"""
        with self.assertRaises(UserError):
            self.properties.action_sold()

        self.offers.action_accept()

        self.properties.action_sold()
        self.assertRecordValues(self.properties, [
            {'state': 'sold'}
        ])

        with self.assertRaises(UserError):
            self.env['estate.properties.offer'].create([{
                'partner_id': self.partner.id,
                'property_id': self.properties[0].id,
                'expected_price': 9500,
            }])
