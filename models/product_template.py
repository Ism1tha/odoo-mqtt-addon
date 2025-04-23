from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_robot_transportable = fields.Boolean(string='Is Robot Transportable?', help='Check if this product is robot transportable.')
    material_id = fields.Char(string='Material ID', help='ID of the material for robot transportable items only.')
