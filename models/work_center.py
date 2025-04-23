from odoo import models, fields

class WorkCenter(models.Model):
    _inherit = "mrp.workcenter"

    has_robots = fields.Boolean(string="Has Robots?", help="Check if this Work Center has robots")
    robot_ids = fields.One2many("mqtt_interface.robot", "workcenter_id", string="Robots", help="List of robots in this Work Center")
    topic = fields.Char(string="Topic", help="Factory > Warehouse > Picking Code (e.g., F1 > W1 > PKG1)")
