from odoo import models, fields, api
from datetime import datetime, timedelta

class BackupRetention(models.Model):
    _name = 'backup.retention'
    _description = 'Backup Retention Policy'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    max_age_days = fields.Integer(string="Max Age (Days)", default=30)
    max_count = fields.Integer(string="Max Backups", default=10)
    apply_to = fields.Selection([
        ('full', 'Full Backups'),
        ('incremental', 'Incremental Backups'),
        ('all', 'All Backups')
    ], default='all')

    def enforce_policies(self):
        for policy in self.search([('active', '=', True)]):
            threshold_date = datetime.now() - timedelta(days=policy.max_age_days)
            backups = self.env['backup.job'].search([
                ('create_date', '<', threshold_date),
                ('backup_type', 'in', self._get_backup_types(policy.apply_to))
            ], order='create_date asc')

            # Age-based cleanup
            if backups and policy.max_age_days:
                backups.filtered_domain([
                    ('create_date', '<', threshold_date)
                ]).unlink()

            # Count-based cleanup
            if policy.max_count:
                excess = self.env['backup.job'].search_count([]) - policy.max_count
                if excess > 0:
                    backups[:excess].unlink()