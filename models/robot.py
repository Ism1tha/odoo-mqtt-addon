from odoo import models, fields

class Robot(models.Model):
    _name = "mqtt_interface.robot"
    identifier = fields.Char(string="Robot Identifier")
    name = fields.Char(string="Robot Name")
    workcenter_id = fields.Many2one('mrp.workcenter', string="Workcenter")
