# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from odoo import fields, models


class EvaluatePartner(models.TransientModel):
    _name = "evaluate_partner"
    _description = "Evaluate Partner"

    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        relation="evaluate_partner_res_partner_rel",
        column1="wizard_id",
        column2="partner_id",
        default=lambda self: self._default_partner_ids(),
    )
    type_ids = fields.Many2many(
        comodel_name="partner_evaluation_type",
        string="Evaluation Types",
        required=True,
        relation="evaluate_partner_type_rel",
        column1="wizard_id",
        column2="type_id",
    )

    def _default_partner_ids(self):
        # Default to active_id or active_ids from context
        active_ids = self.env.context.get("active_ids", [])
        return self.env["res.partner"].browse(active_ids)

    def action_confirm(self):
        for record in self.sudo():
            result = record._confirm()
        return result

    def _confirm(self):
        # Create partner evaluation for each type
        evaluation_ids = []
        for evaluation_type in self.type_ids:
            for partner in self.partner_ids:
                evaluation = self.env["partner_evaluation"].create(
                    {
                        "partner_id": partner.id,
                        "type_id": evaluation_type.id,
                        "date": date.today(),
                        "date_start": evaluation_type.date_start_offset_id.get_duration(
                            date.today()
                        ),
                        "date_end": evaluation_type.date_end_offset_id.get_duration(
                            date.today()
                        ),
                    }
                )
                evaluation_ids.append(evaluation.id)
        # Open the created evaluations
        return {
            "name": "Partner Evaluations",
            "type": "ir.actions.act_window",
            "res_model": "partner_evaluation",
            "view_mode": "tree,form",
            "domain": [("id", "in", evaluation_ids)],
        }
