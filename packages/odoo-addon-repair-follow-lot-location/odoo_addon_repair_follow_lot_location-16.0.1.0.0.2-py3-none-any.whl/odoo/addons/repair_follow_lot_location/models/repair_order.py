# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RepairOrder(models.Model):

    _inherit = "repair.order"

    follow_lot_location = fields.Boolean(
        help="When enabled, the repair's location is kept in sync with the "
        "current internal location of the linked lot/serial.",
        default=False,
        index=True,
    )
