# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date
from math import ceil

from odoo import _, api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class PartnerBatchEvaluation(models.Model):
    _name = "partner_batch_evaluation"
    _description = "Partner Batch Evaluation"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
        "mixin.transaction_date_duration",
        "mixin.many2one_configurator",
        "mixin.localdict",
    ]
    _order = "date desc, id"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_multiple_approval_page = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _method_to_run_from_wizard = "action_cancel"

    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    type_id = fields.Many2one(
        comodel_name="partner_evaluation_type",
        string="Type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date = fields.Date(
        string="Date",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda r: r._default_date(),
    )
    allowed_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Allowed Partners",
        compute="_compute_allowed_partner_ids",
        store=False,
        compute_sudo=True,
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="rel_partner_batch_evaluation_2_partner",
        column1="batch_id",
        column2="partner_id",
    )
    evaluation_ids = fields.One2many(
        string="Evaluations",
        comodel_name="partner_evaluation",
        inverse_name="batch_id",
        readonly=True,
    )

    # queue
    queue_job_batch_id = fields.Many2one(
        string="Queue Job Batch",
        comodel_name="queue.job.batch",
        readonly=True,
        copy=False,
    )

    queue_job_ids = fields.One2many(
        string="Queue Jobs",
        comodel_name="queue.job",
        related="queue_job_batch_id.job_ids",
        store=False,
    )
    queue_job_batch_state = fields.Selection(
        string="Queue Job Batch State",
        related="queue_job_batch_id.state",
        store=True,
    )

    @api.model
    def _default_date(self):
        return date.today()

    def action_load_partner(self):
        for record in self.sudo():
            record._load_partner()

    def action_confirm_evaluation(self):
        for record in self.sudo():
            record._confirm_evaluation()

    def action_start_evaluation(self):
        for record in self.sudo():
            record._start_evaluation()

    def action_approve_evaluation(self):
        for record in self.sudo():
            record._approve_evaluation()

    def action_reject_evaluation(self):
        for record in self.sudo():
            record._reject_evaluation()

    def action_cancel_evaluation(self):
        for record in self.sudo():
            record._cancel_evaluation()

    def action_restart_evaluation(self):
        for record in self.sudo():
            record._restart_evaluation()

    def _create_job_batch(self, batch_name):
        self.ensure_one()
        batch = self.env["queue.job.batch"].get_new_batch(batch_name)
        self.write(
            {
                "queue_job_batch_id": batch.id,
            }
        )

    def _confirm_evaluation(self):
        self.ensure_one()
        batch_name = "Confirm batch evaluation ID %s" % (self.id)
        self._create_job_batch(batch_name)
        data_per_split = 100
        effected_evaluations = self.evaluation_ids.filtered(lambda r: r.state == "open")
        num_split = ceil(len(effected_evaluations) / data_per_split)
        for split_number in range(1, num_split + 1):
            evaluations = effected_evaluations[
                (data_per_split * split_number)
                - data_per_split : split_number * data_per_split
            ]
            description = "Confirm batch evaluation ID %s split number %s" % (
                self.id,
                split_number,
            )
            evaluations.with_context(job_batch=self.queue_job_batch_id).with_delay(
                description=_(description)
            ).action_confirm()
            self.queue_job_batch_id.enqueue()

    def _start_evaluation(self):
        self.ensure_one()
        batch_name = "Start batch evaluation ID %s" % (self.id)
        self._create_job_batch(batch_name)
        data_per_split = 100
        effected_evaluations = self.evaluation_ids.filtered(
            lambda r: r.state == "draft"
        )
        num_split = ceil(len(effected_evaluations) / data_per_split)
        for split_number in range(1, num_split + 1):
            evaluations = effected_evaluations[
                (data_per_split * split_number)
                - data_per_split : split_number * data_per_split
            ]
            description = "Start batch evaluation ID %s split number %s" % (
                self.id,
                split_number,
            )
            evaluations.with_context(job_batch=self.queue_job_batch_id).with_delay(
                description=_(description)
            ).action_open()
            self.queue_job_batch_id.enqueue()

    def _approve_evaluation(self):
        self.ensure_one()
        batch_name = "Approve batch evaluation ID %s" % (self.id)
        self._create_job_batch(batch_name)
        data_per_split = 100
        effected_evaluations = self.evaluation_ids.filtered(
            lambda r: r.state == "confirm"
        )
        num_split = ceil(len(effected_evaluations) / data_per_split)
        for split_number in range(1, num_split + 1):
            evaluations = effected_evaluations[
                (data_per_split * split_number)
                - data_per_split : split_number * data_per_split
            ]
            description = "Approve batch evaluation ID %s split number %s" % (
                self.id,
                split_number,
            )
            evaluations.with_context(job_batch=self.queue_job_batch_id).with_delay(
                description=_(description)
            ).action_approve_approval()
            self.queue_job_batch_id.enqueue()

    def _reject_evaluation(self):
        self.ensure_one()
        batch_name = "Reject batch evaluation ID %s" % (self.id)
        self._create_job_batch(batch_name)
        data_per_split = 100
        effected_evaluations = self.evaluation_ids.filtered(
            lambda r: r.state == "confirm"
        )
        num_split = ceil(len(effected_evaluations) / data_per_split)
        for split_number in range(1, num_split + 1):
            evaluations = effected_evaluations[
                (data_per_split * split_number)
                - data_per_split : split_number * data_per_split
            ]
            description = "Reject batch evaluation ID %s split number %s" % (
                self.id,
                split_number,
            )
            evaluations.with_context(job_batch=self.queue_job_batch_id).with_delay(
                description=_(description)
            ).action_reject_approval()
            self.queue_job_batch_id.enqueue()

    def _cancel_evaluation(self):
        self.ensure_one()
        batch_name = "Cancel batch evaluation ID %s" % (self.id)
        self._create_job_batch(batch_name)
        data_per_split = 100
        effected_evaluations = self.evaluation_ids.filtered(
            lambda r: r.state != "cancel"
        )
        num_split = ceil(len(effected_evaluations) / data_per_split)
        for split_number in range(1, num_split + 1):
            evaluations = effected_evaluations[
                (data_per_split * split_number)
                - data_per_split : split_number * data_per_split
            ]
            description = "Cancel batch evaluation ID %s split number %s" % (
                self.id,
                split_number,
            )
            evaluations.with_context(job_batch=self.queue_job_batch_id).with_delay(
                description=_(description)
            ).action_cancel()
            self.queue_job_batch_id.enqueue()

    def _restart_evaluation(self):
        self.ensure_one()
        batch_name = "Restart batch evaluation ID %s" % (self.id)
        self._create_job_batch(batch_name)
        data_per_split = 100
        effected_evaluations = self.evaluation_ids.filtered(
            lambda r: r.state == "cancel"
        )
        num_split = ceil(len(effected_evaluations) / data_per_split)
        for split_number in range(1, num_split + 1):
            evaluations = effected_evaluations[
                (data_per_split * split_number)
                - data_per_split : split_number * data_per_split
            ]
            description = "Restart batch evaluation ID %s split number %s" % (
                self.id,
                split_number,
            )
            evaluations.with_context(job_batch=self.queue_job_batch_id).with_delay(
                description=_(description)
            ).action_restart()
            self.queue_job_batch_id.enqueue()

    @api.depends("type_id")
    def _compute_allowed_partner_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="res.partner",
                    method_selection=record.type_id.partner_selection_method,
                    manual_recordset=record.type_id.partner_ids,
                    domain=record.type_id.partner_domain,
                    python_code=record.type_id.partner_python_code,
                )
            record.allowed_partner_ids = result

    def action_open_evaluation(self):
        for record in self.sudo():
            result = record._open_evaluation()
        return result

    def _open_evaluation(self):
        self.ensure_one()
        action = self.env.ref(
            "ssi_partner_evaluation.partner_evaluation_action"
        ).read()[0]
        action["domain"] = [("batch_id", "=", self.id)]
        action["context"] = {
            "default_type_id": self.type_id.id,
            "default_date": self.date,
            "default_date_start": self.date_start,
            "default_date_end": self.date_end,
            "default_batch_id": self.id,
        }
        return action

    def _load_partner(self):
        self.ensure_one()
        self.write({"partner_ids": [(6, 0, self.allowed_partner_ids.ids)]})

    @ssi_decorator.post_done_action()
    def _create_evaluations(self):
        self.ensure_one()
        Evaluation = self.env["partner_evaluation"]
        for partner in self.partner_ids:
            data = {
                "type_id": self.type_id.id,
                "partner_id": partner.id,
                "date": self.date,
                "date_start": self.date_start,
                "date_end": self.date_end,
                "batch_id": self.id,
            }
            Evaluation.create(data)

    @ssi_decorator.post_cancel_action()
    def _delete_evaluation(self):
        self.ensure_one()
        self.evaluation_ids.unlink()

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "cancel_ok",
            "done_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
