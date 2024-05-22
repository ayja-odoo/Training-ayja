from odoo import fields, models
from odoo import api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class estate_property(models.Model):
    _name = "estate.property"
    _description = "it has the estate property "
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    avaliable_from = fields.Date(copy = False,default = fields.Date.today()+relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True,copy = False)
    bedrooms = fields.Integer(default='2')
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    Active = fields.Boolean()
    #it is a virtual function 
    offer_ids= fields.One2many("estate.property.offer","property_id")

    tag_ids = fields.Many2many('estate.property.tag') 
    
    salesman_id = fields.Many2one('res.users',default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner',copy = False )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    
    garden_orientation = fields.Selection(
        string = 'Type', # it is like lable in html 
        selection=[('North','north'), ('South','south') , ('East','east'), ('West','west') ]
        )
    state = fields.Selection(
        string = 'Select',
        selection = [('new','New'),('offer_received','Offer Received'),('offer_accepted','Offer Accepted'),('cancelled','Cancelled'),('sold','Sold')],
        default = "new"
    )
    total_area = fields.Float(compute="_compute_total")
    best_price =fields.Float(compute="_compute_best")
    # color = fields.Integer("Color Index")
    
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 1)', 'Price Should be Posotive'),
        ('check_selling_price', 'CHECK(selling_price >= 1)', 'Price Should be Posotive')
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for prop in self:
            prop.total_area= prop.living_area + prop.garden_area

    @api.depends("offer_ids.price")
    def _compute_best(self):
        self.best_price = max(self.offer_ids.mapped("price")) if self.offer_ids else 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_area = 10
            self.garden_orientation = 'North'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.onchange("offer_ids")
    def _onchange_state(self):
        if(self.offer_ids):
            self.state='offer_received'
        else:
            self.state= 'new'
    
    def action_cancle(self):
            if self.state == 'sold':
                raise UserError("Sold properties cannot be Cancelled!")
            else : 
                self.state= 'cancelled'
                
    def action_sold(self):
            if self.state == 'cancelled':
                raise UserError("Cancelled properties cannot be Sold!")
            else:
                self.state= 'sold'

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for prop in self:
            if (
                not float_is_zero(prop.selling_price, precision_rounding=0.01)
                and float_compare(prop.selling_price, prop.expected_price * 90.0 / 100.0, precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must increase the offer price if you want to accept this offer."
                )

    @api.ondelete(at_uninstall=False)
    def ondelete(self):
        if(self.state != ['new','cancelled']):
            raise UserError("Only New and Cancelled state properties can be deleted")
        return super().ondelete(state)

