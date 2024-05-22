from odoo import fields, models
from odoo import api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class estate_property_offer(models.Model):
    _name = "estate.property.offer"
    _description = "it has the estate property offers"
    _order = "price desc"

    price = fields.Float()
    partner_id = fields.Many2one("res.partner",required = True)
    status = fields.Selection(
        selection = [('accepted','Accepted'),('refused','Refused')],
        copy = False,
        default = False
    )
    property_id = fields.Many2one("estate.property", required = True,readonly = True)
    validity = fields.Integer(default =7, string="Validity (day)", store=True )
    date_deadline = fields.Date("Deadline", compute='_compute_date',inverse="_inverse_date_deadline", store=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id")

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price >= 1)', 'Price Should be Posotive')
    ]

    @api.depends('validity','date_deadline','create_date')
    def _compute_date(self):
        for d in self:
            date = d.create_date.date() if d.create_date else fields.Date.today()
            d.date_deadline = date + relativedelta(days=d.validity)

    def _inverse_date_deadline(self):
        for dv in self:
            datee = dv.create_date.date() if dv.create_date else fields.Date.today()
            dv.validity = (dv.date_deadline - datee).days


    def action_yes(self):
        self.property_id.selling_price = self.price 
        self.property_id.buyer_id = self.partner_id
        self.property_id.state = 'offer_accepted'
        for i in self.property_id.offer_ids:
            i.status='refused'
        self.status='accepted'
        return True
        

    def action_no(self):
        self.status = 'refused'
        return True
    

    # here vals is which we are going to create 
    @api.model
    def create(self,vals):
        if(self.env["estate.property"].browse(vals['property_id']).best_price > vals['price']):
            raise UserError("Offer should be higher then previous offers ")
        return super().create(vals)