# -*- coding: utf-8 -*-

from odoo import models, fields


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    # ===========================
    # FIELDS
    # ===========================

    has_robots = fields.Boolean(
        string="Has Robots",
        help="Indicates if this work center has robots configured"
    )
    robot_ids = fields.One2many(
        comodel_name="mqtt_integration.robot",
        inverse_name="workcenter_id",
        string="Robots",
        help="Robots assigned to this work center"
    )
    mqtt_topic = fields.Char(
        string="MQTT Topic",
        help="MQTT topic for robot communication"
    )
