from odoo import models, fields

class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    has_robots = fields.Boolean(
        string="Has Robots",
        help="Indicates whether this Work Center includes robots for automated tasks."
    )

    robot_ids = fields.One2many(
        comodel_name="mqtt_integration.robot",
        inverse_name="workcenter_id",
        string="Robots",
        help="Robots assigned to this Work Center for automation."
    )

    mqtt_topic = fields.Char(
        string="MQTT Topic",
        help="MQTT topic used for robot messaging. Format: Factory > Warehouse > Picking Code (e.g., F1 > W1 > PKG1)"
    )
