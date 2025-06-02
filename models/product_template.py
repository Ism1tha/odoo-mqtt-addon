# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ===========================
    # FIELDS
    # ===========================

    mqtt_product_type = fields.Selection(
        selection=[
            ('action', 'Action'),
            ('result', 'Transportable Product'),
            ('material', 'Material'),
        ],
        string="MQTT Product Type",
        help="Defines how this product is used in MQTT processing"
    )
    mqtt_material_binary = fields.Char(
        string="MQTT Material Binary",
        help="Binary representation for MQTT material communication"
    )
    mqtt_material_product_result_id = fields.Many2one(
        comodel_name='product.product',
        string="Result Product",
        help="Product that results from processing this material"
    )
    mqtt_material_product_result_qty = fields.Float(
        string="Result Product Quantity",
        help="Quantity of result product generated from this material"
    )

    # ===========================
    # ACTIONS
    # ===========================

    def action_start_mqtt_processing_on_productions(self):
        """Start MQTT processing on all productions using this product template."""
        productions = self.env['mrp.production'].search([
            ('product_id.product_tmpl_id', '=', self.id)
        ])
        for production in productions:
            production.action_start_mqtt_processing()