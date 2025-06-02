# -*- coding: utf-8 -*-

from odoo import models, fields


class MqttRobot(models.Model):
    _name = "mqtt_integration.robot"
    _description = "MQTT Robot"
    _rec_name = 'name'

    # ===========================
    # FIELDS
    # ===========================

    identifier = fields.Char(
        string="Robot Identifier",
        required=True,
        help="Unique identifier used for MQTT communication"
    )
    name = fields.Char(
        string="Robot Name",
        required=True,
        help="Human-readable name for the robot"
    )
    workcenter_id = fields.Many2one(
        comodel_name='mrp.workcenter',
        string="Work Center",
        ondelete='cascade',
        help="Work center where this robot is assigned"
    )