from odoo.tests import tagged, TransactionCase

@tagged('post_install', '-at_install')
class TestMappingWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.wizard = self.env['migration.mapping.wizard'].create({
            'source_model': 'res.partner',
            'destination_model': 'res.partner'
        })

    def test_field_mapping_validation(self):
        """Test required fields"""
        with self.assertRaises(ValidationError):
            self.wizard.write({
                'field_mapping': [(0, 0, {
                    'source_field': 'name',
                    'destination_field': False  # Invalid
                })]
            })

    def test_transformation_rules(self):
        valid = self.wizard.write({
            'field_mapping': [(0, 0, {
                'source_field': 'name',
                'destination_field': 'name',
                'transformation': 'trim'
            })]
        })
        self.assertTrue(valid)