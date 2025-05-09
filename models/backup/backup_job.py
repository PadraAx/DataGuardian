from odoo import models, fields, api

class BackupJob(models.Model):
    _name = 'backup.job'
    _description = 'Backup Job'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Backup Name', required=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('done', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='draft',
        tracking=True,
    )
    # === New Fields Added ===
    backup_type = fields.Selection(
        selection=[
            ('full', 'Full Backup'),
            ('incremental', 'Incremental'),
            ('partial', 'Partial (Model/Record)'),
        ],
        default='full',
        required=True,
    )
    model_ids = fields.Many2many(
        'ir.model',
        string='Target Models',
        help="For partial backups: select specific models",
    )
    record_ids = fields.Text(
        string='Record Filter',
        help="JSON list of IDs for record-level backups",
    )
    encryption = fields.Boolean(
        string='Enable Encryption',
        default=True,
    )
    compression = fields.Selection(
        selection=[
            ('none', 'None'),
            ('gzip', 'Gzip (Fast)'),
            ('zip', 'ZIP (Strong)'),
        ],
        default='gzip',
    )
    backup_size = fields.Float(string='Size (MB)', readonly=True)
    storage_location = fields.Char(string='Storage Path', readonly=True)
    log = fields.Text(string='Execution Log', readonly=True)
    # === End New Fields ===

    def action_start(self):
        """Start backup job"""
        self.write({'state': 'running'})
        # Actual backup logic will go here
        return True
    
    def action_start(self):
    """Real backup execution"""
    self.ensure_one()
    if self.backup_type == 'full':
        self._execute_full_backup()
    # ...
    def action_start(self):
    self.ensure_one()
    self.write({'state': 'running'})
    try:
        if self.backup_type == 'full':
            backup_path = self._execute_full_backup()
        elif self.backup_type == 'incremental':
            backup_path = self._execute_incremental_backup()
        else:
            backup_path = self._execute_partial_backup()
        
        self.write({
            'state': 'done',
            'storage_location': backup_path,
            'backup_size': self._get_file_size(backup_path),
            'log': f"Backup completed at {fields.Datetime.now()}"
        })
    except Exception as e:
        self.write({
            'state': 'failed',
            'log': f"Backup failed: {str(e)}"
        })
        raise UserError(_('Backup failed. Check logs for details.'))

def _execute_full_backup(self):
    """Generate full database dump"""
    # Implement using Odoo's db.backup or custom logic
    return "/path/to/backup.zip"

def _execute_incremental_backup(self):
    """Only backup changes since last backup"""
    # Implement delta backup logic
    return "/path/to/incremental.zip"
import csv
import base64
from io import StringIO

def _generate_csv_backup(self, model_name):
    """Generate CSV backup for specific model"""
    model = self.env[model_name]
    data = model.search_read([], fields=list(model.fields_get_keys()))

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)

    return base64.b64encode(output.getvalue().encode('utf-8'))

def action_export_csv(self):
    self.ensure_one()
    if not self.model_ids:
        raise UserError(_("No models selected for CSV export"))

    attachments = []
    for model in self.model_ids:
        csv_data = self._generate_csv_backup(model.model)
        attachments.append({
            'name': f"{model.model}.csv",
            'type': 'binary',
            'datas': csv_data,
            'res_model': 'backup.job',
            'res_id': self.id,
        })

    self.env['ir.attachment'].create(attachments)
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'message': f"Exported {len(attachments)} CSV files",
            'type': 'success',
            'sticky': False,
        }
    }