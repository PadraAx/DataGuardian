from odoo import models, api

class BackupJob(models.Model):
    _name = 'backup.job'
    _inherit = ['mail.thread']
    _description = 'Backup Job'
    
    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        if operation == 'unlink' and not self.env.is_admin():
            if raise_exception:
                raise AccessError("Only admins can delete backup jobs")
            return False
        return super().check_access_rights(operation, raise_exception)