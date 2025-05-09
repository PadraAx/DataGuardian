from odoo import models, fields

class WebhookEndpoint(models.Model):
    _name = 'webhook.endpoint'
    _description = 'Registered Webhooks'

    url = fields.Char(string='Callback URL', required=True)
    event_type = fields.Selection([
        ('backup_started', 'Backup Started'),
        ('restore_started', 'Restore Started'),
        ('bulk_complete', 'Bulk Operations Complete')
    ], required=True)
    secret_key = fields.Char(string='Auth Key')
    from odoo import models, fields

class WebhookEndpoint(models.Model):
    _name = 'webhook.endpoint'
    _description = 'Registered Webhooks'

    url = fields.Char(required=True)
    event_type = fields.Selection([
        ('backup_started', 'Backup Started'),
        ('restore_started', 'Restore Started'), 
        ('bulk_complete', 'Bulk Complete')
    ], required=True)
    secret_key = fields.Char()