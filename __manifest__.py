# -*- coding: utf-8 -*-
{
    "name": "Odoo MQTT Interface",
    "summary": "Integrate MQTT communication with Odoo for robotic automation.",
    "description": """
        A module to integrate MQTT communication with Odoo for robotic automation.

        This module provides:
        - MQTT integration for manufacturing processes
        - Robot management and configuration
        - Production order automation through MQTT
        - Work center MQTT topic configuration
        - Product template MQTT settings
    """,
    "author": "Ismael Semmar Galvez",
    "website": "https://github.com/Ism1tha/odoo-mqtt-module.git",
    "category": "Manufacturing",
    "version": "1.0.0",
    "license": "GPL-3",
    "depends": [
        "base",
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/work_center_view.xml",
        "views/robot_view.xml",
        "views/res_config_settings.xml",
        "views/product_template_view.xml",
        "views/production_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mqtt_integration/static/src/js/form_renderer_patch.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
