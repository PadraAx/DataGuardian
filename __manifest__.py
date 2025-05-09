{
    'name': 'DataGuardian',
    'version': '17.0.1.0',
    'summary': 'All-in-One Backup, Restore & Migration',
    'description': """
    Enterprise-grade data protection for Odoo 17
    ===========================================
    - Military-grade AES-256 encryption
    - Cross-version migration tools
    - Granular backup/restore (DB/App/Record-level)
    - Multi-cloud storage support (AWS, Google, FTP)
    - GDPR/ISO27001 compliant auditing
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base', 
        'web',
        'mail',
        'queue_job'  # For long-running operations
    ],
    'category': 'Tools',
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/groups.xml',
        'security/audit_rules.xml',
        'security/data_protection.xml',
        
        # Data
        'data/ir_cron.xml',
        'data/error_codes.xml',
        'data/mail_templates.xml',
        'data/migration_templates.xml',
        'data/res_config.xml',
        
        # Views
        'views/backup_views.xml',
        'views/migration_views.xml',
        'views/wizard_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'data_guardian/static/src/js/backup.js',
            'data_guardian/static/src/js/migration.js',
            'data_guardian/static/src/css/styles.scss',
        ],
        'web.assets_qweb': [
            'data_guardian/static/src/xml/*.xml',
        ],
    },
    'external_dependencies': {
        'python': [
            'cryptography>=3.3',
            'boto3>=1.20',
            'psycopg2-binary>=2.9'
        ],
    },
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'price': 0,  # Free community edition
    'currency': 'EUR',
    'support': 'support@yourcompany.com',
}
'external_dependencies': {
    'python': [
        'boto3>=1.20',
        'google-cloud-storage>=2.0'
    ]
},
'data': [
    'views/portal_templates.xml'
]
'external_dependencies': {
    'python': [
        'azure-storage-blob>=12.0'
    ]
}
'data': [
    'data/ir_cron.xml',
    # ... other files
]
'data': [
    'views/openapi_templates.xml'  # For Swagger UI integration
]
'data': [
    'security/ir.model.access.csv',
    'security/security_rules.xml'
]
'external_dependencies': {
    'python': ['requests']
}

'data': [
    'views/templates.xml',
    'views/backup_views.xml'
]
'data': [
    'data/config_parameters.xml'
]