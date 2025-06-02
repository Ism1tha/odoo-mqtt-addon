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
            
            complete_mqtt_topic = f"{mqtt_topic}/{production.selected_robot_id.identifier}"
            
            binary_payload = production._generate_binary_payload()
            
            task_data = production._create_api_task(complete_mqtt_topic, binary_payload)
            
            if task_data:
                production.write({
                    'state': 'mqtt_processing',
                    'mqtt_task_id': task_data.get('id'),
                    'mqtt_binary_payload': binary_payload
                })
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
        """Generate binary payload from BOM components"""
        if not self.bom_id or not self.bom_id.bom_line_ids:
            return '000000'
        
        result_binary = [0] * 6
        
        for line in self.bom_id.bom_line_ids:
            component_binary = line.product_id.product_tmpl_id.mqtt_material_binary or ''
            if component_binary:
                # Ensure 6-bit format and pad/truncate as needed
                component_binary = component_binary.zfill(6)[-6:]
                for i, bit in enumerate(component_binary):
                    if bit == '1':
                        result_binary[i] = 1
        
        return ''.join(str(bit) for bit in result_binary)

    def _create_api_task(self, mqtt_topic, binary_payload):
        config = self.env['ir.config_parameter'].sudo()
        
        host = config.get_param('mqtt_integration.mqtt_api_host', 'localhost')
        port = config.get_param('mqtt_integration.mqtt_api_port', '3000')
        auth_enabled = config.get_param('mqtt_integration.mqtt_api_authentication_enabled', 'False')
        auth_password = config.get_param('mqtt_integration.mqtt_api_authentication_password', '')
        
        url = f"http://{host}:{port}/api/tasks"
        
        headers = {'Content-Type': 'application/json'}
        if auth_enabled == 'True' and auth_password:
            headers['Authorization'] = f'Bearer {auth_password}'
        
        data = {
            'odooProductionId': str(self.id),
            'mqttTopic': mqtt_topic,
            'binaryPayload': binary_payload,
            'priority': 'normal'
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _logger.error(f"Failed to create MQTT task for production {self.id}: {e}")
            return None

    def _delete_api_task(self, task_id):
        """Delete a task from the Node.js API"""
        config = self.env['ir.config_parameter'].sudo()
        
        host = config.get_param('mqtt_integration.mqtt_api_host', 'localhost')
        port = config.get_param('mqtt_integration.mqtt_api_port', '3000')
        auth_enabled = config.get_param('mqtt_integration.mqtt_api_authentication_enabled', 'False')
        auth_password = config.get_param('mqtt_integration.mqtt_api_authentication_password', '')
        
        url = f"http://{host}:{port}/api/tasks/{task_id}"
        
        headers = {}
        if auth_enabled == 'True' and auth_password:
            headers['Authorization'] = f'Bearer {auth_password}'
        
        try:
            response = requests.delete(url, headers=headers, timeout=10)
            response.raise_for_status()
            _logger.info(f"Successfully deleted MQTT task {task_id} from API for production {self.id}")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                _logger.warning(f"MQTT task {task_id} not found in API (may have been already processed or deleted)")
                return True
            else:
                _logger.error(f"HTTP error deleting MQTT task {task_id} from API for production {self.id}: {e}")
                return False
        except requests.exceptions.ConnectionError as e:
            _logger.error(f"Connection error deleting MQTT task {task_id} from API for production {self.id}: {e}")
            return False
        except requests.exceptions.Timeout as e:
            _logger.error(f"Timeout error deleting MQTT task {task_id} from API for production {self.id}: {e}")
            return False
        except Exception as e:
            _logger.error(f"Unexpected error deleting MQTT task {task_id} from API for production {self.id}: {e}")
            return False

    def action_stop_mqtt_processing(self):
        for production in self:
            if production.state != 'mqtt_processing':
                continue
            
            if production.mqtt_task_id:
                success = production._delete_api_task(production.mqtt_task_id)
                if not success:
                    _logger.error(f"Failed to delete MQTT task {production.mqtt_task_id} from API for production {production.id}")
                    raise UserError(f'Failed to delete MQTT task from API. Please try again or contact the administrator.')
            
            for wo in production.workorder_ids:
                wo.write({'state': 'pending'})
            
            production.write({
                'state': 'draft',
                'mqtt_task_id': False,
                'mqtt_binary_payload': False
            })

    def _handle_task_completion(self):
        """Handle successful task completion from MQTT API with stock management"""
        for production in self:
            if production.state != 'mqtt_processing':
                _logger.warning(f"Production {production.id} is not in mqtt_processing state, current state: {production.state}")
                continue
            
            try:
                # Handle stock movements first - decrease materials and increase result product
                production._handle_stock_movements()
                
                # Ensure production has proper material allocation
                if production.state == 'mqtt_processing':
                    # Check material availability and assign if needed
                    production.action_assign()
                
                # Complete all work orders properly
                for wo in production.workorder_ids:
                    production._complete_work_order(wo)
                
                # Mark production as done
                production.write({'state': 'done'})
                
                _logger.info(f"Production {production.id} completed successfully via MQTT task {production.mqtt_task_id}")
                
            except Exception as e:
                _logger.error(f"Error completing production {production.id}: {e}")
                # Mark as failed instead of resetting to draft
                production.write({'state': 'cancel'})
                raise

    def _handle_stock_movements(self):
        """Handle stock movements for completed MQTT production"""
        for production in self:
            try:
                # Only process if we have a BOM with components
                if not production.bom_id or not production.bom_id.bom_line_ids:
                    _logger.warning(f"No BOM or components found for production {production.id}")
                    return
                
                # Process each BOM component (materials)
                for bom_line in production.bom_id.bom_line_ids:
                    material_product = bom_line.product_id
                    
                    # Skip if not a material type
                    if material_product.product_tmpl_id.mqtt_product_type != 'material':
                        continue
                    
                    # Decrease material stock by 1 unit
                    production._decrease_material_stock(material_product, 1.0)
                    
                    # Get result product from material configuration
                    result_product = material_product.product_tmpl_id.mqtt_material_product_result_id
                    result_qty = material_product.product_tmpl_id.mqtt_material_product_result_qty or 1.0
                    
                    if result_product:
                        # Increase result product stock
                        production._increase_result_stock(result_product, result_qty)
                        _logger.info(f"Stock updated for production {production.id}: decreased {material_product.name}, increased {result_product.name} by {result_qty}")
                
            except Exception as e:
                _logger.error(f"Error handling stock movements for production {production.id}: {e}")
                raise

    def _decrease_material_stock(self, product, quantity):
        """Decrease material stock by specified quantity"""
        try:
            # Get stock locations - use internal location and virtual production location
            stock_location = self.env.ref('stock.stock_location_stock')
            # Use virtual production location or create a temporary one
            try:
                production_location = self.env.ref('stock.location_production')
            except:
                # Fallback to virtual production location
                production_location = self.env['stock.location'].search([
                    ('usage', '=', 'production')
                ], limit=1)
                if not production_location:
                    # Create a virtual production location if none exists
                    production_location = self.env['stock.location'].create({
                        'name': 'Virtual Production',
                        'usage': 'production',
                        'company_id': self.company_id.id,
                    })
            
            # Create stock move to decrease material
            stock_move = self.env['stock.move'].create({
                'name': f'MQTT Material Consumption - {self.name}',
                'product_id': product.id,
                'product_uom_qty': quantity,
                'product_uom': product.uom_id.id,
                'location_id': stock_location.id,
                'location_dest_id': production_location.id,
                'origin': self.name,
                'company_id': self.company_id.id,
            })
            
            # Confirm and process the move
            stock_move._action_confirm()
            stock_move._action_assign()
            # Manually set quantity done on move lines  
            for move_line in stock_move.move_line_ids:
                move_line.write({'quantity': quantity})
            stock_move._action_done()
            
            _logger.info(f"Decreased stock for material {product.name} by {quantity} units")
            
        except Exception as e:
            _logger.error(f"Error decreasing material stock for product {product.name}: {e}")
            raise

    def _increase_result_stock(self, product, quantity):
        """Increase result product stock by specified quantity"""
        try:
            # Get stock locations
            stock_location = self.env.ref('stock.stock_location_stock')
            # Use virtual production location or create a temporary one
            try:
                production_location = self.env.ref('stock.location_production')
            except:
                # Fallback to virtual production location
                production_location = self.env['stock.location'].search([
                    ('usage', '=', 'production')
                ], limit=1)
                if not production_location:
                    # Create a virtual production location if none exists
                    production_location = self.env['stock.location'].create({
                        'name': 'Virtual Production',
                        'usage': 'production',
                        'company_id': self.company_id.id,
                    })
            
            # Create stock move to increase result product
            stock_move = self.env['stock.move'].create({
                'name': f'MQTT Production Output - {self.name}',
                'product_id': product.id,
                'product_uom_qty': quantity,
                'product_uom': product.uom_id.id,
                'location_id': production_location.id,
                'location_dest_id': stock_location.id,
                'origin': self.name,
                'company_id': self.company_id.id,
            })
            
            # Confirm and process the move
            stock_move._action_confirm()
            stock_move._action_assign()
            # Manually set quantity done on move lines
            for move_line in stock_move.move_line_ids:
                move_line.write({'quantity': quantity})
            stock_move._action_done()
            
            _logger.info(f"Increased stock for result product {product.name} by {quantity} units")
            
        except Exception as e:
            _logger.error(f"Error increasing result stock for product {product.name}: {e}")
            raise

    def _handle_task_failure(self, error_message):
        """Handle task failure from MQTT API"""
        for production in self:
            if production.state != 'mqtt_processing':
                _logger.warning(f"Production {production.id} is not in mqtt_processing state, current state: {production.state}")
                continue
            
            # Mark work orders as cancelled
            for wo in production.workorder_ids:
                if wo.state in ['pending', 'ready', 'progress']:
                    wo.write({'state': 'cancel'})
            
            # Reset production to draft state
            production.write({'state': 'draft'})
            
            _logger.error(f"Production {production.id} failed via MQTT task {production.mqtt_task_id}: {error_message}")

    def _handle_production_completion(self):
        """Handle production completion notification from MQTT API"""
        for production in self:
            if production.state == 'mqtt_processing':
                production._handle_task_completion()

    def _handle_production_failure(self):
        """Handle production failure notification from MQTT API"""
        for production in self:
            if production.state == 'mqtt_processing':
                production._handle_task_failure("Production failed during robot execution")

    def _complete_work_order(self, work_order):
        """Properly complete a work order by progressing through states"""
        try:
            _logger.info(f"Completing work order {work_order.id} (current state: {work_order.state})")
            
            # If work order is waiting for components, try to assign materials
            if work_order.state == 'waiting':
                # Make sure production has materials allocated
                if self.reservation_state != 'assigned':
                    self.action_assign()
                
                # Force work order to ready state since we've handled stock moves manually
                work_order.write({'state': 'ready'})
                _logger.info(f"Work order {work_order.id} moved from waiting to ready")
            
            # If ready, start the work order
            if work_order.state == 'ready':
                try:
                    work_order.button_start()
                    _logger.info(f"Work order {work_order.id} started")
                except Exception as e:
                    _logger.warning(f"Could not start work order {work_order.id} normally: {e}. Setting to progress.")
                    work_order.write({'state': 'progress'})
            
            # If in progress, finish it
            if work_order.state == 'progress':
                try:
                    # Set working state if needed
                    if hasattr(work_order, 'working_state') and work_order.working_state != 'done':
                        work_order.button_finish()
                        _logger.info(f"Work order {work_order.id} finished")
                    else:
                        # Directly set to done if no working state management
                        work_order.write({'state': 'done'})
                        _logger.info(f"Work order {work_order.id} set to done")
                except Exception as e:
                    _logger.warning(f"Could not finish work order {work_order.id} normally: {e}. Setting to done.")
                    work_order.write({'state': 'done'})
            
            # Final check - if still not done, force completion
            if work_order.state != 'done':
                # Force state to done if all other methods failed
                work_order.write({'state': 'done'})
                _logger.info(f"Work order {work_order.id} forced to done state")
                
        except Exception as e:
            _logger.error(f"Error completing work order {work_order.id}: {e}")
            # As fallback, just set to done
            work_order.write({'state': 'done'})