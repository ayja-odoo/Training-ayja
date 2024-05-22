from odoo import fields, models

class estate_property_tag(models.Model):
    _name = "estate.property.tag"
    _description = "it has the estate property tags"
    _order = "name"
    
    _sql_constraints = [
        ('check_property_tag_name', 'UNIQUE(name)', 'Name must be unique')
    ]

    name = fields.Char(required = True)
    color = fields.Integer("Color Index")