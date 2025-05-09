def test_csv_mapping(self):
    wizard = self.env['migration.wizard'].create({...})
    wizard.map_field('partner.name', 'csv_name')
    self.assertEqual(wizard.mapped_fields[0].odoo_field, 'name')
    
    from odoo.tests import tagged, TransactionCase

@tagged('post_install', '-at_install')
class TestMigrationJob(TransactionCase):
    def setUp(self):
        super().setUp()
        self.migration = self.env['migration.job'].create({
            'name': 'Test Migration',
            'destination_model_id': self.env.ref('base.model_res_partner').id,
        })

    def test_preset_application(self):
        preset = self.env['migration.preset'].create({
            'name': 'Partner Template',
            'model_id': self.env.ref('base.model_res_partner').id,
            'field_mapping': '{"name": "name", "email": "email"}'
        })
        preset.apply_to_job(self.migration)
        self.assertEqual(self.migration.field_mapping, preset.field_mapping)

    def test_dry_run_mode(self):
        self.migration.write({
            'source_type': 'csv',
            'test_mode': True,
            'field_mapping': '{"name": "name"}'
        })
        result = self.migration._execute_migration()
        self.assertTrue(result)
        self.assertEqual(self.migration.state, 'running')