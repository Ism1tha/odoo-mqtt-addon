from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mqtt_api_host = fields.Char(
        string="MQTT API Host",
        config_parameter="mqtt_integration.mqtt_api_host",
        default="localhost",
        help="The hostname or IP address of the MQTT broker."
    )
    mqtt_api_port = fields.Integer(
        string="MQTT API Port",
        config_parameter="mqtt_integration.mqtt_api_port",
        default=1883,
        help="The port number for connecting to the MQTT broker."
    )
