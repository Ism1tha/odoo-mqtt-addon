# -*- coding: utf-8 -*-

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MQTTAPIController(http.Controller):
    _inherit = 'http.controller'

    # ===========================
    # API ENDPOINTS
    # ===========================

    @http.route('/mqtt-integration/update-production-status', type='http', auth='none', methods=['POST'], csrf=False)
    def update_production_status(self, **kwargs):
        """Update manufacturing order status from MQTT API with improved queue integration."""
        try:
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                _logger.error(f"Invalid JSON data in production status update: {e}")
                return self._error_response('Invalid JSON format')
            
            validation_result = self._validate_request_data(data)
            if validation_result:
                return validation_result
            
            production_id = data['productionId']
            status = data['status'] 
            task_id = data.get('taskId')
            
            _logger.info(f"Processing status update - Production: {production_id}, Status: {status}, Task: {task_id}")
            
            production = self._get_production(production_id)
            if isinstance(production, dict):
                return production
            
            try:
                request.env.cr.execute("SELECT id FROM mrp_production WHERE id = %s FOR UPDATE NOWAIT", (production.id,))
                
                production = production.sudo()
                
                if status == 'done' and production.state == 'done':
                    _logger.info(f"Production {production_id} already completed, skipping duplicate request")
                    return self._success_response('Production already completed')
                
                if status == 'failed' and production.state in ('cancel', 'draft'):
                    _logger.info(f"Production {production_id} already failed/cancelled, skipping duplicate request")
                    return self._success_response('Production already failed/cancelled')
                
                if task_id and production.mqtt_task_id != task_id:
                    _logger.warning(f"Task ID mismatch for production {production_id}: expected {production.mqtt_task_id}, got {task_id}")
                    return self._error_response('Task ID mismatch')
                
                success = self._process_status_update(production, status, task_id)
                if not success:
                    return self._error_response(f'Failed to process status: {status}')
                    
            except Exception as lock_error:
                _logger.warning(f"Could not acquire lock for production {production_id}: {lock_error}")
                return self._success_response('Production update already in progress')
            
            _logger.info(f"Successfully updated production {production_id} to status {status}")
            return self._success_response('Production status updated successfully')
            
        except Exception as e:
            _logger.error(f"Unexpected error in production status update: {str(e)}")
            return self._error_response(f'Internal server error: {str(e)}')

    # ===========================
    # VALIDATION METHODS
    # ===========================

    def _validate_request_data(self, data):
        """Validate the request data format and required fields."""
        if not data:
            _logger.error("Empty data received in production status update")
            return self._error_response('No data provided')
        
        required_fields = ['productionId', 'status']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            _logger.error(f"Missing required fields: {missing_fields}")
            return self._error_response(f'Missing required fields: {", ".join(missing_fields)}')
        
        valid_statuses = ['done', 'failed']
        if data['status'] not in valid_statuses:
            _logger.error(f"Invalid status '{data['status']}', must be one of: {valid_statuses}")
            return self._error_response(f'Invalid status. Valid options: {", ".join(valid_statuses)}')
        
        return None

    # ===========================
    # PRODUCTION METHODS
    # ===========================

    def _get_production(self, production_id):
        """Get production record with error handling."""
        try:
            env = request.env(user=1)
            production = env['mrp.production'].browse(int(production_id))
            
            if not production.exists():
                _logger.error(f"Production {production_id} not found")
                return self._error_response(f'Production {production_id} not found')
            
            return production
            
        except ValueError:
            _logger.error(f"Invalid production ID format: {production_id}")
            return self._error_response('Invalid production ID format')
        except Exception as e:
            _logger.error(f"Error retrieving production {production_id}: {e}")
            return self._error_response('Failed to retrieve production')

    def _process_status_update(self, production, status, task_id):
        """Process the status update for the production."""
        try:
            if status == 'done':
                production._handle_task_completion()
                _logger.info(f"Production {production.id} completed successfully via task {task_id}")
                return True
            elif status == 'failed':
                error_msg = f'Task {task_id} failed during robot execution'
                production._handle_task_failure(error_msg)
                _logger.info(f"Production {production.id} marked as failed via task {task_id}")
                return True
            else:
                _logger.error(f"Unhandled status '{status}' for production {production.id}")
                return False
                
        except Exception as e:
            _logger.error(f"Error processing status update for production {production.id}: {e}")
            try:
                if status == 'done':
                    production.write({'state': 'cancel'})
                    _logger.info(f"Production {production.id} marked as cancelled due to completion error")
            except:
                pass
            return False

    # ===========================
    # RESPONSE METHODS
    # ===========================

    def _success_response(self, message):
        """Generate a standardized success response."""
        response = json.dumps({
            'status': 'success',
            'message': message,
            'timestamp': self._get_timestamp()
        })
        return response

    def _error_response(self, message):
        """Generate a standardized error response."""
        response = json.dumps({
            'status': 'error', 
            'message': message,
            'timestamp': self._get_timestamp()
        })
        return response

    def _get_timestamp(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    # ===========================
    # HEALTH CHECK ENDPOINTS
    # ===========================

    @http.route('/mqtt-integration/health', type='json', auth='none', methods=['GET'], csrf=False)
    def health_check(self, **kwargs):
        """Health check endpoint for MQTT API integration."""
        try:
            env = request.env(user=1)
            
            production_count = env['mrp.production'].search_count([])
            
            return {
                'status': 'healthy',
                'message': 'MQTT Integration addon is running',
                'timestamp': self._get_timestamp(),
                'database_accessible': True,
                'production_records': production_count
            }
        except Exception as e:
            _logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'System error: {str(e)}',
                'timestamp': self._get_timestamp(),
                'database_accessible': False
            }
