# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json

class OpenAPISchema(http.Controller):
    @http.route('/api/backup/schema', auth='public', methods=['GET'], type='http')
    def generate_schema(self):
        """Generate OpenAPI 3.0 schema for backup API"""
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "DataGuardian Backup API",
                "version": "1.0.0",
                "description": "Enterprise backup/restore API endpoints"
            },
            "paths": {
                "/api/backup/start": {
                    "post": {
                        "summary": "Trigger new backup",
                        "parameters": [
                            {
                                "name": "backup_type",
                                "in": "query",
                                "required": True,
                                "schema": {
                                    "type": "string",
                                    "enum": ["full", "incremental", "partial"]
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Backup job started",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "job_id": {"type": "integer"},
                                                "status": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/restore/execute": {
                    "post": {
                        "summary": "Execute restore",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "backup_id": {"type": "integer"},
                                            "scope": {
                                                "type": "string",
                                                "enum": ["full", "models", "records"]
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "202": {
                                "description": "Restore job accepted"
                            }
                        }
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "api_key": {
                        "type": "apiKey",
                        "name": "Authorization",
                        "in": "header"
                    }
                }
            }
        }

        return request.make_response(
            json.dumps(schema),
            headers=[('Content-Type', 'application/json')]
        )