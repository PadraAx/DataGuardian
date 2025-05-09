# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class BackupAPI(http.Controller):

    @http.route('/api/backup/start', type='json', auth='api_key', methods=['POST'])
    def start_backup(self, backup_type, model_ids=None, **kwargs):
        """Initiate backup through API
        Args:
            backup_type (str): full/incremental/partial
            model_ids (list): Required for partial backups
        Returns:
            dict: {job_id: int, status: str}
        """
        try:
            vals = {
                'name': f"API Backup {fields.Datetime.now()}",
                'backup_type': backup_type,
            }
            if backup_type == 'partial' and model_ids:
                vals['model_ids'] = [(6, 0, model_ids)]
            
            job = request.env['backup.job'].sudo().create(vals)
            job.action_start()
            
            return {
                'job_id': job.id,
                'status': 'started',
                'timestamp': fields.Datetime.now()
            }
        except Exception as e:
            _logger.error(f"API Backup Failed: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                mimetype='application/json'
            )

    @http.route('/api/restore/execute', type='json', auth='api_key', methods=['POST'])
    def execute_restore(self, backup_id, scope='full', model_ids=None, **kwargs):
        """Initiate restore through API
        Args:
            backup_id (int): ID of backup.job to restore
            scope (str): full/models/records
            model_ids (list): Required for model-level restore
        """
        try:
            backup = request.env['backup.job'].sudo().browse(backup_id)
            if not backup.exists():
                raise ValueError("Backup not found")
                
            vals = {
                'name': f"API Restore {fields.Datetime.now()}",
                'backup_id': backup.id,
                'restore_type': 'partial' if scope != 'full' else 'full',
            }
            
            if scope == 'models' and model_ids:
                vals['model_ids'] = [(6, 0, model_ids)]
                
            job = request.env['restore.job'].sudo().create(vals)
            job.action_start()
            
            return {
                'restore_id': job.id,
                'status': 'started',
                'backup_source': backup.storage_location
            }
        except Exception as e:
            _logger.error(f"API Restore Failed: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                mimetype='application/json'
            )

    @http.route('/api/backup/status/<int:job_id>', type='http', auth='api_key', methods=['GET'])
    def check_status(self, job_id, model_type='backup'):
        """Check job status
        Args:
            job_id (int): ID of backup/restore job
            model_type (str): 'backup' or 'restore'
        """
        model = 'backup.job' if model_type == 'backup' else 'restore.job'
        job = request.env[model].sudo().browse(job_id)
        
        if not job.exists():
            return Response(
                json.dumps({'error': 'Job not found'}),
                status=404,
                mimetype='application/json'
            )
            
        return Response(
            json.dumps({
                'state': job.state,
                'progress': job.progress,
                'log': job.log
            }),
            mimetype='application/json'
        )
        
# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request, Response
from odoo.exceptions import AccessDenied
import json
import logging
from datetime import datetime, timedelta
from functools import wraps

_logger = logging.getLogger(__name__)

# Rate limiting store (in production use Redis instead)
API_CALLS = {}

def rate_limited(max_calls=10, period=60):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ip = request.httprequest.remote_addr
            now = datetime.now()
            
            # Initialize call tracking
            if ip not in API_CALLS:
                API_CALLS[ip] = {
                    'count': 0,
                    'reset_time': now + timedelta(seconds=period)
                }
            
            # Reset counter if period expired
            if now > API_CALLS[ip]['reset_time']:
                API_CALLS[ip] = {
                    'count': 0,
                    'reset_time': now + timedelta(seconds=period)
                }
            
            # Check limit
            if API_CALLS[ip]['count'] >= max_calls:
                raise AccessDenied(_("API rate limit exceeded"))
            
            API_CALLS[ip]['count'] += 1
            return func(*args, **kwargs)
        return wrapper
    return decorator

class BackupAPI(http.Controller):

    def _trigger_webhooks(self, event_type, payload):
        """Notify registered webhooks"""
        webhooks = request.env['webhook.endpoint'].sudo().search([
            ('event_type', '=', event_type)
        ])
        for hook in webhooks:
            try:
                requests.post(
                    hook.url,
                    json=payload,
                    headers={'Authorization': hook.secret_key},
                    timeout=5
                )
            except Exception as e:
                _logger.error(f"Webhook failed to {hook.url}: {str(e)}")

    @http.route('/api/backup/bulk', type='json', auth='api_key', methods=['POST'])
    @rate_limited(max_calls=5, period=300)  # 5 requests per 5 minutes
    def bulk_operations(self, operations):
        """Execute multiple backup/restore operations
        Args:
            operations (list): [
                {
                    "operation": "backup|restore",
                    "params": { ... }  # Same as individual endpoints
                }
            ]
        Returns:
            list: Results for each operation
        """
        if len(operations) > 10:
            return Response(
                json.dumps({'error': 'Max 10 operations per batch'}),
                status=400
            )
        
        results = []
        for op in operations:
            try:
                if op['operation'] == 'backup':
                    result = self.start_backup(**op['params'])
                elif op['operation'] == 'restore':
                    result = self.execute_restore(**op['params'])
                else:
                    result = {'error': 'Invalid operation'}
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        
        # Trigger webhook for bulk completion
        self._trigger_webhooks('bulk_complete', {
            'timestamp': fields.Datetime.now(),
            'success_count': len([r for r in results if 'error' not in r])
        })
        
        return results

    @http.route('/api/backup/start', type='json', auth='api_key', methods=['POST'])
    @rate_limited()
    def start_backup(self, backup_type, model_ids=None, **kwargs):
        """Initiate backup through API"""
        try:
            vals = {
                'name': f"API Backup {fields.Datetime.now()}",
                'backup_type': backup_type,
            }
            if backup_type == 'partial' and model_ids:
                vals['model_ids'] = [(6, 0, model_ids)]
            
            job = request.env['backup.job'].sudo().create(vals)
            job.action_start()
            
            # Trigger webhook
            self._trigger_webhooks('backup_started', {
                'job_id': job.id,
                'backup_type': backup_type
            })
            
            return {
                'job_id': job.id,
                'status': 'started',
                'timestamp': fields.Datetime.now()
            }
        except Exception as e:
            _logger.error(f"API Backup Failed: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                mimetype='application/json'
            )

    @http.route('/api/restore/execute', type='json', auth='api_key', methods=['POST'])
    @rate_limited()
    def execute_restore(self, backup_id, scope='full', model_ids=None, **kwargs):
        """Initiate restore through API"""
        try:
            backup = request.env['backup.job'].sudo().browse(backup_id)
            if not backup.exists():
                raise ValueError("Backup not found")
                
            vals = {
                'name': f"API Restore {fields.Datetime.now()}",
                'backup_id': backup.id,
                'restore_type': 'partial' if scope != 'full' else 'full',
            }
            
            if scope == 'models' and model_ids:
                vals['model_ids'] = [(6, 0, model_ids)]
                
            job = request.env['restore.job'].sudo().create(vals)
            job.action_start()
            
            # Trigger webhook
            self._trigger_webhooks('restore_started', {
                'job_id': job.id,
                'backup_source': backup.storage_location
            })
            
            return {
                'restore_id': job.id,
                'status': 'started',
                'backup_source': backup.storage_location
            }
        except Exception as e:
            _logger.error(f"API Restore Failed: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                mimetype='application/json'
            )

    @http.route('/api/webhook/register', type='json', auth='api_key', methods=['POST'])
    def register_webhook(self, url, event_type, secret_key=None):
        """Register new webhook endpoint
        Args:
            url (str): Callback URL
            event_type (str): Event to subscribe to
            secret_key (str): Optional auth header
        """
        if not url.startswith(('http://', 'https://')):
            return {'error': 'Invalid URL format'}
            
        request.env['webhook.endpoint'].sudo().create({
            'url': url,
            'event_type': event_type,
            'secret_key': secret_key
        })
        return {'status': 'registered'}

    @http.route('/api/backup/status/<int:job_id>', type='http', auth='api_key', methods=['GET'])
    @rate_limited(max_calls=30, period=60)  # More lenient for status checks
    def check_status(self, job_id, model_type='backup'):
        """Check job status"""
        model = 'backup.job' if model_type == 'backup' else 'restore.job'
        job = request.env[model].sudo().browse(job_id)
        
        if not job.exists():
            return Response(
                json.dumps({'error': 'Job not found'}),
                status=404,
                mimetype='application/json'
            )
            
        return Response(
            json.dumps({
                'state': job.state,
                'progress': job.progress,
                'log': job.log
            }),
            mimetype='application/json'
        )