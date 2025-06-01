from odoo import models, fields

class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    has_robots = fields.Boolean(
        string="Has Robots"
    )

    robot_ids = fields.One2many(
        comodel_name="mqtt_integration.robot",
        inverse_name="workcenter_id",
        string="Robots"
    )

    mqtt_topic = fields.Char(
        string="MQTT Topic"
    )
