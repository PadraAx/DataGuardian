# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)

class DataGuardianMain(http.Controller):
    
    @http.route('/backup/dashboard', type='http', auth='user', website=True)
    def backup_dashboard(self, **kw):
        """Main backup dashboard"""
        if not request.env.user.has_group('data_guardian.group_backup_user'):
            raise AccessError(_("You don't have access to this page"))
        
        return request.render('data_guardian.backup_dashboard', {
            'backups': request.env['backup.job'].search([], limit=10),
            'restores': request.env['restore.job'].search([], limit=5),
            'storage_stats': self._get_storage_stats()
        })

    @http.route('/backup/new', type='http', auth='user', website=True)
    def new_backup_wizard(self, **kw):
        """Backup creation wizard"""
        return request.render('data_guardian.backup_wizard_form', {
            'models': request.env['ir.model'].search([('transient', '=', False)]),
            'companies': request.env['res.company'].search([])
        })

    @http.route('/backup/submit', type='http', auth='user', website=True, csrf=True)
    def submit_backup(self, backup_type, model_ids=None, **kw):
        """Handle backup form submission"""
        try:
            vals = {
                'name': kw.get('name', _('New Backup')),
                'backup_type': backup_type,
                'user_id': request.env.user.id
            }
            
            if backup_type == 'partial' and model_ids:
                vals['model_ids'] = [(6, 0, list(map(int, model_ids.split(','))))]
                
            backup = request.env['backup.job'].create(vals)
            backup.action_start()
            
            return request.redirect('/backup/dashboard?success=1')
        except Exception as e:
            _logger.error(f"Backup creation failed: {str(e)}")
            return request.redirect(f'/backup/new?error={str(e)}')

    @http.route('/backup/download/<int:backup_id>', type='http', auth='user')
    def download_backup(self, backup_id, **kw):
        """Download backup file"""
        backup = request.env['backup.job'].browse(backup_id)
        if not backup.exists():
            raise UserError(_("Backup not found"))
            
        return request.make_response(
            backup.file_content,
            headers=[
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', f'attachment; filename="{backup.filename}"')
            ]
        )

    def _get_storage_stats(self):
        """Calculate storage usage statistics"""
        return {
            'total': sum(b.backup_size for b in request.env['backup.job'].search([])),
            'last_week': sum(
                b.backup_size for b in request.env['backup.job'].search([
                    ('create_date', '>=', fields.Datetime.now() - timedelta(days=7))
                ])
            ),
            'by_type': {
                'full': sum(
                    b.backup_size for b in request.env['backup.job'].search([
                        ('backup_type', '=', 'full')
                    ])
                ),
                'incremental': sum(
                    b.backup_size for b in request.env['backup.job'].search([
                        ('backup_type', '=', 'incremental')
                    ])
                )
            }
        }