# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request, Response
from odoo.exceptions import ValidationError
import logging
import hmac
import hashlib
import json

_logger = logging.getLogger(__name__)

class WebhookController(http.Controller):

    @http.route('/webhook/data_guardian', type='json', auth='none', csrf=False, methods=['POST'])
    def handle_inbound_webhook(self, **kwargs):
        """Process incoming webhook notifications"""
        try:
            # 1. Verify signature
            secret = request.env['ir.config_parameter'].sudo().get_param('data_guardian.webhook_secret')
            if secret:
                signature = request.httprequest.headers.get('X-Signature')
                if not signature:
                    _logger.warning("Missing webhook signature")
                    return Response(status=403)
                
                body = request.httprequest.data
                computed = hmac.new(
                    secret.encode(),
                    body,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, computed):
                    _logger.warning("Invalid webhook signature")
                    return Response(status=403)

            # 2. Process payload
            data = request.jsonrequest
            event_type = data.get('event')
            
            # Handle different event types
            if event_type == 'backup_completed':
                self._process_backup_event(data)
            elif event_type == 'restore_completed':
                self._process_restore_event(data)
            else:
                _logger.warning(f"Unknown webhook event: {event_type}")
                return Response(status=400)

            return Response(status=200)
        except Exception as e:
            _logger.error(f"Webhook processing failed: {str(e)}")
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                mimetype='application/json'
            )

    def _process_backup_event(self, data):
        """Handle backup-related webhooks"""
        backup = request.env['backup.job'].sudo().browse(data.get('backup_id'))
        if not backup.exists():
            raise ValidationError(_("Backup not found"))
            
        backup.write({
            'external_status': data.get('status'),
            'log': data.get('log', '')
        })

    def _process_restore_event(self, data):
        """Handle restore-related webhooks"""
        restore = request.env['restore.job'].sudo().browse(data.get('restore_id'))
        if not restore.exists():
            raise ValidationError(_("Restore not found"))
            
        restore.write({
            'external_status': data.get('status'),
            'verification_log': data.get('verification', '')
        })

    @http.route('/webhook/test', type='http', auth='user', methods=['GET'])
    def test_webhook_configuration(self, webhook_id):
        """Test webhook endpoint configuration"""
        webhook = request.env['webhook.endpoint'].sudo().browse(int(webhook_id))
        if not webhook.exists():
            raise ValidationError(_("Webhook not found"))
        
        try:
            test_payload = {
                'event': 'test',
                'message': 'Webhook configuration verified',
                'timestamp': fields.Datetime.now()
            }
            
            headers = {}
            if webhook.secret_key:
                signature = hmac.new(
                    webhook.secret_key.encode(),
                    json.dumps(test_payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Signature'] = signature
            
            response = requests.post(
                webhook.url,
                json=test_payload,
                headers=headers,
                timeout=10
            )
            
            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'response_code': response.status_code,
                    'response_text': response.text
                }),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')],
                status=500
            )