from odoo import models, fields, api
import subprocess
import logging
_logger = logging.getLogger(__name__)

class DisasterRecoveryTest(models.Model):
    _name = 'disaster.recovery.test'
    _description = 'Automated Disaster Recovery Test'

    name = fields.Char(default="DR Test", required=True)
    test_type = fields.Selection([
        ('full', 'Full System Restore'),
        ('partial', 'Critical Models Only')
    ], default='full')
    backup_id = fields.Many2one('backup.job', required=True)
    test_db = fields.Char(string="Test Database", default="dr_test_db")
    success = fields.Boolean(readonly=True)
    log = fields.Text(readonly=True)

    def execute_test(self):
        try:
            # 1. Create test DB
            subprocess.run([
                'createdb', self.test_db
            ], check=True)

            # 2. Restore backup
            restore_cmd = [
                'pg_restore',
                '-d', self.test_db,
                self.backup_id.storage_location
            ]
            result = subprocess.run(
                restore_cmd,
                capture_output=True,
                text=True
            )

            # 3. Validate
            self.success = result.returncode == 0
            self.log = f"""
            Test executed at {fields.Datetime.now()}
            Command: {' '.join(restore_cmd)}
            Output: {result.stdout}
            Errors: {result.stderr}
            """
        except Exception as e:
            _logger.error(f"DR Test failed: {str(e)}")
            raise