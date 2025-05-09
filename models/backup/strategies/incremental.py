from odoo import models, fields, api
import hashlib
import json

class IncrementalBackup(models.Model):
    _name = 'backup.incremental'
    _description = 'Incremental Backup Strategy'

    def compute_diff(self, last_backup_date):
        """Identify changed records since last backup"""
        diff = {}
        for model in self.env['ir.model'].search([('transient', '=', False)]):
            records = self.env[model.model].search([
                ('write_date', '>', last_backup_date)
            ])
            diff[model.model] = [(r.id, self._record_hash(r)) for r in records]
        return json.dumps(diff)

    def _record_hash(self, record):
        """Generate content hash for change detection"""
        data = record.read()[0]
        return hashlib.sha256(str(data).encode()).hexdigest()