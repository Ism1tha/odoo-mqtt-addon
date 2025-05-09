from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mqtt_api_host = fields.Char(
        string="MQTT Broker Host",
        config_parameter="mqtt_integration.mqtt_api_host",
        default="localhost",
        help="Hostname or IP address of the MQTT broker. (e.g., mqtt.example.com)"
    )

    mqtt_api_port = fields.Integer(
        string="MQTT Broker Port",
        config_parameter="mqtt_integration.mqtt_api_port",
        default=1883,
        help="Port number used to connect to the MQTT broker (default is 1883)."
    )