import requests
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mqtt_task_id = fields.Char("MQTT Task ID", readonly=True)
    mqtt_binary_payload = fields.Char("Binary Payload", readonly=True)
    selected_robot_id = fields.Many2one("mqtt_integration.robot", string="Selected Robot")
    available_robot_ids = fields.Many2many("mqtt_integration.robot", compute="_compute_available_robots", string="Available Robots")
    show_start_mqtt = fields.Boolean(compute='_compute_show_start_mqtt')
    is_mqtt_product = fields.Boolean(compute='_compute_is_mqtt_product')

    state = fields.Selection(
        selection_add=[('mqtt_processing', 'MQTT Processing')]
    )

    @api.depends('workorder_ids.workcenter_id.robot_ids')
    def _compute_available_robots(self):
        for record in self:
            robots = self.env['mqtt_integration.robot']
            if record.workorder_ids:
                for wo in record.workorder_ids:
                    if wo.workcenter_id and wo.workcenter_id.robot_ids:
                        robots |= wo.workcenter_id.robot_ids
            record.available_robot_ids = robots

    @api.onchange('workorder_ids')
    def _onchange_workorder_ids(self):
        if self.selected_robot_id and self.selected_robot_id not in self.available_robot_ids:
            self.selected_robot_id = False

    @api.depends('product_id.product_tmpl_id.mqtt_product_type', 'state', 'mqtt_task_id')
    def _compute_show_start_mqtt(self):
        for record in self:
            record.show_start_mqtt = (
                record.product_id
                and record.product_id.product_tmpl_id
                and record.product_id.product_tmpl_id.mqtt_product_type == 'action'
                and record.state in ('draft', 'confirmed', 'progress')
                and not record.mqtt_task_id
            )

    def _compute_is_mqtt_product(self):
        for record in self:
            record.is_mqtt_product = (
                record.product_id
                and record.product_id.product_tmpl_id
                and record.product_id.product_tmpl_id.mqtt_product_type == 'action'
            )

    @api.constrains('workorder_ids', 'product_id')
    def _check_mqtt_workorder_limit(self):
        for production in self:
            if (production.is_mqtt_product and 
                production.state not in ('draft', 'cancel') and
                len(production.workorder_ids) > 1):
                raise ValidationError('MQTT products can only have one work order.')

    def action_confirm(self):
        if self._should_block_action():
            raise UserError('Manufacturing actions are blocked when MQTT processing is enabled for this product type.')
        if self.is_mqtt_product and len(self.workorder_ids) > 1:
            raise UserError('MQTT products can only have one work order.')
        return super().action_confirm()

    def button_plan(self):
        if self._should_block_action():
            raise UserError('Manufacturing actions are blocked when MQTT processing is enabled for this product type.')
        return super().button_plan()

    def action_assign(self):
        if self._should_block_action():
            raise UserError('Manufacturing actions are blocked when MQTT processing is enabled for this product type.')
        return super().action_assign()

    def button_mark_done(self):
        if self._should_block_action():
            raise UserError('Manufacturing actions are blocked when MQTT processing is enabled for this product type.')
        return super().button_mark_done()

    def action_cancel(self):
        if self._should_block_action():
            raise UserError('Manufacturing actions are blocked when MQTT processing is enabled for this product type.')
        return super().action_cancel()

    def _should_block_action(self):
        return (
            self.product_id
            and self.product_id.product_tmpl_id
            and self.product_id.product_tmpl_id.mqtt_product_type == 'action'
            and self.state in ('confirmed', 'progress')
            and not self.mqtt_task_id
        )

    def action_start_mqtt_processing(self):
        for production in self:
            if not production.product_id.product_tmpl_id.mqtt_product_type == 'action':
                raise UserError('Product must be of type "Action" for MQTT processing.')
            
            if len(production.workorder_ids) > 1:
                raise UserError('MQTT products can only have one work order.')
            
            if production.state == 'draft':
                production.action_confirm()
            
            if not production.workorder_ids:
                raise UserError('No work orders found for this production.')
            
            if not production.bom_id:
                raise UserError('No Bill of Materials (BOM) defined.')
            
            work_center = production.workorder_ids[0].workcenter_id
            if not work_center.robot_ids:
                raise UserError(f'No robots assigned to work center "{work_center.name}".')
            
            if not production.selected_robot_id:
                raise UserError('Please select a robot before starting MQTT processing.')
            
            if production.selected_robot_id not in work_center.robot_ids:
                raise UserError('Selected robot is not assigned to the work center.')
            
            mqtt_topic = production._get_mqtt_topic()
            if not mqtt_topic:
                raise UserError('No MQTT topic configured for work centers.')
            
            binary_payload = production._generate_binary_payload()
            
            task_data = production._create_api_task(mqtt_topic, binary_payload)
            
            if task_data:
                production.write({
                    'state': 'mqtt_processing',
                    'mqtt_task_id': task_data.get('id'),
                    'mqtt_binary_payload': binary_payload
                })
                
                production.message_post(
                    body=f"MQTT Task created - ID: {task_data.get('id')} | Payload: {binary_payload} | Topic: {mqtt_topic} | Robot: {production.selected_robot_id.name}",
                    message_type='comment'
                )
            else:
                raise UserError('Failed to create MQTT task.')

    def _get_mqtt_topic(self):
        for wo in self.workorder_ids:
            if wo.workcenter_id and wo.workcenter_id.mqtt_topic:
                _logger.info(f"Found MQTT topic '{wo.workcenter_id.mqtt_topic}' from work center '{wo.workcenter_id.name}'")
                return wo.workcenter_id.mqtt_topic.strip()
        
        if self.bom_id and self.bom_id.operation_ids:
            for operation in self.bom_id.operation_ids:
                if operation.workcenter_id and operation.workcenter_id.mqtt_topic:
                    _logger.info(f"Found MQTT topic '{operation.workcenter_id.mqtt_topic}' from BOM operation work center '{operation.workcenter_id.name}'")
                    return operation.workcenter_id.mqtt_topic.strip()
        
        _logger.warning(f"No MQTT topic found for production {self.id}. Work orders: {len(self.workorder_ids)}, BOM operations: {len(self.bom_id.operation_ids) if self.bom_id else 0}")
        return None

    def _generate_binary_payload(self):
        if not self.bom_id or not self.bom_id.bom_line_ids:
            return '000000'
        
        result_binary = [0] * 6
        
        for line in self.bom_id.bom_line_ids:
            comp_binary = line.product_id.product_tmpl_id.mqtt_material_binary or ''
            if comp_binary:
                comp_binary = comp_binary.zfill(6)[-6:]
                for i, bit in enumerate(comp_binary):
                    if bit == '1':
                        result_binary[i] = 1
        
        return ''.join(str(bit) for bit in result_binary)

    def _create_api_task(self, mqtt_topic, binary_payload):
        config = self.env['ir.config_parameter'].sudo()
        
        host = config.get_param('mqtt_integration.mqtt_api_host', 'localhost')
        port = config.get_param('mqtt_integration.mqtt_api_port', '3000')
        
        url = f"http://{host}:{port}/api/tasks"
        
        data = {
            'odooProductionId': str(self.id),
            'mqttTopic': mqtt_topic,
            'binaryPayload': binary_payload,
            'priority': 'normal',
            'robotId': self.selected_robot_id.identifier if self.selected_robot_id else None,
            'metadata': {
                'productionName': self.name,
                'productName': self.product_id.name,
                'workCenterName': self.workorder_ids[0].workcenter_id.name if self.workorder_ids else None,
                'robotName': self.selected_robot_id.name if self.selected_robot_id else None
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _logger.error(f"Failed to create MQTT task for production {self.id}: {e}")
            return None

    def action_stop_mqtt_processing(self):
        for production in self:
            if production.state != 'mqtt_processing':
                continue
            
            for wo in production.workorder_ids:
                wo.write({'state': 'pending'})
            
            production.write({
                'state': 'draft',
                'mqtt_task_id': False,
                'mqtt_binary_payload': False
            })
            
            production.message_post(
                body=f"MQTT Processing stopped - Production returned to draft state",
                message_type='comment'
            )