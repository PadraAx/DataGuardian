from odoo import models, fields, api

class MigrationPreset(models.Model):
    _name = 'migration.preset'
    _description = 'Field Mapping Preset'

    name = fields.Char(string='Template Name', required=True)
    source_type = fields.Selection([
        ('odoo', 'Odoo'),
        ('csv', 'CSV/Excel'),
        ('sql', 'SQL'),
    ], required=True)
    model_id = fields.Many2one(
        'ir.model', 
        string='Target Model',
        required=True
    )
    field_mapping = fields.Text(
        string='Field Mapping JSON',
        default='{}',
        help='Stores source→target field mappings as JSON'
    )
    is_global = fields.Boolean(
        string='Global Template',
        default=False,
        help='Available to all companies'
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )

    def apply_to_job(self, job):
        job.write({
            'field_mapping': self.field_mapping,
            'mapping_preset_id': self.id
        })