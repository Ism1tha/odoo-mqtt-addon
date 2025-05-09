from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mqtt_product_type = fields.Selection([
        ('action', 'Action'),
        ('result', 'Transportable Product'),
        ('material', 'Material'),
    ], string="MQTT Product Type", help="Type of product for MQTT integration")

    mqtt_material_binary = fields.Char(
        string="MQTT Material Binary",
        help="6-digit binary string sent to the robot, only for transportable products"
    )

    mqtt_material_product_result_id = fields.Many2one(
        comodel_name='product.product',
        string="Result Product",
        help="Result product that receives +1 in stock when this material's position is selected"
    )

    mqtt_material_product_result_qty = fields.Float(
        string="Result Product Quantity",
        help="Quantity of the result product to be added to stock when this material's position is selected"
    )

    def action_start_mqtt_processing_on_productions(self):
        productions = self.env['mrp.production'].search([('product_id.product_tmpl_id', '=', self.id)])
        for production in productions:
            production.action_start_mqtt_processing()