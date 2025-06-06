# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ===========================
    # MQTT API CONFIGURATION FIELDS
    # ===========================

    mqtt_api_host = fields.Char(
        string="MQTT API Host",
        config_parameter="mqtt_integration.mqtt_api_host",
        default="localhost",
        help="Hostname or IP address of the MQTT API server (e.g., localhost, api.example.com)"
    )
    mqtt_api_port = fields.Integer(
        string="MQTT API Port",
        config_parameter="mqtt_integration.mqtt_api_port",
        default=3000,
        help="Port number used to connect to the MQTT API server (default is 3000)"
    )
    mqtt_api_authentication_enabled = fields.Boolean(
        string="Enable Authentication",
        config_parameter="mqtt_integration.mqtt_api_authentication_enabled",
        default=False,
        help="Enable authentication for the MQTT API server"
    )
    mqtt_api_authentication_password = fields.Char(
        string="Authentication Password",
        config_parameter="mqtt_integration.mqtt_api_authentication_password",
        help="Password for authenticating with the MQTT API server"
    )
