# -*- coding: utf-8 -*-

from odoo import models, Command


class Property(models.Model):
    _inherit = "estate.property"

    def action_mark_sold(self):
        res = super().action_mark_sold()
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        for record in self:
            values = self._prepare_account_move_values(journal, record)
            self.env["account.move"].create(values)
        return res

    def _prepare_account_move_values(self, journal, record):
        record.ensure_one()
        values = {
            "partner_id": record.buyer_id.id,
            "move_type": "out_invoice",
            "journal_id": journal.id,
            "invoice_line_ids": [
                Command.create({
                    "name": record.name,
                    "quantity": 1.0,
                    "price_unit": record.selling_price * 6.0 / 100.0,
                }),
                Command.create({
                    "name": "Administrative fees",
                    "quantity": 1.0,
                    "price_unit": 100.0,
                }),
            ],
        }
        return values
