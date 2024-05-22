from odoo import fields, models
from odoo import api

class estate_property_type(models.Model):
    _name = "estate.property.type"
    _description = "it has the estate property type"
    _order = "sequence,name"

    name = fields.Char(required=True)
    property_ids=fields.One2many("estate.property","property_type_id")
    sequence = fields.Integer('Sequence') # it is for the swquence 
    offer_ids=fields.One2many("estate.property.offer","property_type_id")
    offer_count=fields.Integer(compute="_compute_count")

    _sql_constraints = [
        ('check_property_type_name', 'UNIQUE(name)', 'Name must be unique')
    ]

    @api.depends("offer_ids")
    def _compute_count(self):
        for it in self:
            it.offer_count= len(it.offer_ids)

    # def _compute_count(self):
    #     for of in self:
    #         of.offer_count=0
    #         for it in of.offer_ids:
    #             of.offer_count = of.offer_count+1
    #     return True