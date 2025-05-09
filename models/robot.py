from odoo import models, fields

class MqttRobot(models.Model):
    _name = "mqtt_integration.robot"
    _description = "MQTT Robot"
    
    identifier = fields.Char(
        string="Robot Identifier",
        required=True,
        help="Unique identifier for the robot (e.g., robot serial number or ID)"
    )

    name = fields.Char(
        string="Robot Name",
        required=True,
        help="Human-readable name for the robot (e.g., Robot A)"
    )

    workcenter_id = fields.Many2one(
        comodel_name='mrp.workcenter',
        string="Work Center",
        help="The work center where this robot is assigned",
        ondelete='cascade'
    )