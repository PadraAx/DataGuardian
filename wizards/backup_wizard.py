class BackupWizard(models.TransientModel):
    def action_start(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'backup.job',
            'res_id': self._create_job().id,
        }