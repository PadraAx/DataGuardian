from odoo import http
from odoo.http import request

class BackupPortal(http.Controller):
    @http.route('/backup/docs', type='http', auth='user')
    def documentation(self):
        return request.render('data_guardian.portal_docs', {
            'docs': {
                'backup': request.env['ir.model'].search([('model', '=', 'backup.job')]),
                'restore': request.env['ir.model'].search([('model', '=', 'restore.job')])
            }
        })