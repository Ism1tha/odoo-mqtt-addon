from odoo import models, fields, api
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_start(self):
        if self._should_block_workorder_action():
            raise UserError(
                'Individual work order operations are blocked when MQTT processing is enabled. '
                'Please use "Start MQTT Processing" button on the production order instead.'
            )
        return super().button_start()

    def button_finish(self):
        if self._should_block_workorder_action():
            raise UserError(
                'Individual work order operations are blocked when MQTT processing is enabled. '
                'MQTT processing will handle work order completion automatically.'
            )
        return super().button_finish()

    def button_pending(self):
        if self._should_block_workorder_action():
            raise UserError(
                'Individual work order operations are blocked when MQTT processing is enabled. '
                'Please use "Start MQTT Processing" button on the production order instead.'
            )
        return super().button_pending()

    def button_done(self):
        if self._should_block_workorder_action():
            raise UserError(
                'Individual work order operations are blocked when MQTT processing is enabled. '
                'MQTT processing will handle work order completion automatically.'
            )
        return super().button_done()

    def action_cancel(self):
        if self._should_block_workorder_action():
            raise UserError(
                'Individual work order operations are blocked when MQTT processing is enabled. '
                'Please stop MQTT processing first if you need to cancel operations.'
            )
        return super().action_cancel()

    def _should_block_workorder_action(self):
        production = self.production_id
        if not production:
            return False
        
        is_action_product = (
            production.product_id
            and production.product_id.product_tmpl_id
            and production.product_id.product_tmpl_id.mqtt_product_type == 'action'
        )
        
        should_use_mqtt = (
            is_action_product
            and production.state in ('confirmed', 'progress')
            and not production.mqtt_task_id
        )
        
        is_mqtt_processing = production.state == 'mqtt_processing'
        
        if should_use_mqtt or is_mqtt_processing:
            _logger.info(f"Blocking work order {self.id} action - Production {production.id} uses MQTT processing")
            return True
            
        return False
