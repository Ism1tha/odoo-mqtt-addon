import json
from odoo import models, fields, api
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    show_start_mqtt = fields.Boolean(compute='_compute_show_start_mqtt')

    mqtt_workorder_states = fields.Text("MQTT Work Order States Backup")
    mqtt_initial_state = fields.Selection(selection='_selection_state', string="Initial State")

    state = fields.Selection(
        selection_add=[('mqtt_processing', 'MQTT Processing')]
    )

    def _selection_state(self):
        """Dynamically returns available state selections."""
        return self._fields['state'].selection

    @api.depends('product_id.product_tmpl_id.mqtt_product_type')
    def _compute_show_start_mqtt(self):
        for record in self:
            record.show_start_mqtt = (
                record.product_id
                and record.product_id.product_tmpl_id
                and record.product_id.product_tmpl_id.mqtt_product_type == 'action'
            )

    def mqtt_process(self):
        """Example processing logic for MQTT binary generation."""
        for production in self:
            product_tmpl = production.product_id.product_tmpl_id
            if product_tmpl.mqtt_product_type == 'action':
                bom = production.bom_id
                if not bom:
                    continue
                result_binary = [0] * 6
                for line in bom.bom_line_ids:
                    comp_tmpl = line.product_id.product_tmpl_id
                    bin_str = comp_tmpl.mqtt_material_binary or ''
                    bin_str = bin_str.zfill(6)[-6:]
                    for idx, char in enumerate(bin_str):
                        if char == '1':
                            result_binary[idx] = 1
                result_binary_str = ''.join(str(bit) for bit in result_binary)
                production.message_post(
                    body=f"MQTT: Resultant binary: {result_binary_str}",
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )

    def action_start_mqtt_processing(self):
        for production in self:
            work_orders = production.workorder_ids
            if not work_orders:
                raise UserError('A work order is required to start MQTT processing.')

            work_orders_to_start = work_orders.filtered(lambda wo: wo.state in ('pending', 'ready'))
            if not work_orders_to_start:
                raise UserError('No work order in a startable state.')

            wo_states = {str(wo.id): wo.state for wo in work_orders}
            production.mqtt_workorder_states = json.dumps(wo_states)


            production.mqtt_initial_state = production.state

            work_orders_to_start[0].button_start()
            production.state = 'mqtt_processing'

    def action_stop_mqtt_processing(self):
        for production in self:
            if production.state == 'mqtt_processing':
                for wo in production.workorder_ids:
                    if hasattr(wo, 'button_pending'):
                        wo.button_pending()
                    wo.write({'state': 'ready'})
                production.write({'state': 'confirmed'})
