from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Reals Estate Property Type"


    name = fields.Char("Type", required=True)