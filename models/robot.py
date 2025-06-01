from odoo import models, fields

class MqttRobot(models.Model):
    _name = "mqtt_integration.robot"
    _description = "MQTT Robot"
    
    identifier = fields.Char(
        string="Robot Identifier",
        required=True
    )

    name = fields.Char(
        string="Robot Name",
        required=True
    )

    workcenter_id = fields.Many2one(
        comodel_name='mrp.workcenter',
        string="Work Center",
        ondelete='cascade'
    )