{
    "name": "Hospital Management System",
    "summary": "Odoo 16 Development",
    "version": "1.0", 
    "application": True, 
    'author': "Cris-aian Vergara",
    'website': "https://www.hospital.com",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/patient.xml",
    ],
    "installable": True,
    'license': 'LGPL-3',
}