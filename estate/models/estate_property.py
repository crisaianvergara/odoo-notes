from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    def _default_date_availability(self):
        """Show availability date in 3 months from today"""
        return fields.Date.context_today(self) + relativedelta(months=3)
    

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Available From", copy=False, default=lambda self: self._default_date_availability())
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        string="Status",
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new"
    )

    # Relational
    # Many2one
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    # Users
    # Many2one
    user_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    # Many2many
    tag_ids = fields.Many2many("estate.property.tag", string="Property Tag")
    # One2many
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # Computed fields
    total_area = fields.Integer(compute="_compute_total_area", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")
    # Constraints
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "The expected price must be strictly positive"),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The offer price must be positive"),
    ]


    # Computed fields functions
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        """Compute total area"""
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        """Get the best price and set the best price is equal to 0.0 when offers are not available"""
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price")) if record.offer_ids else 0.0


    @api.onchange("garden", "garden_area", "garden_orientation")
    def _onchange_garden_area_garden_orientation(self):
        self.garden_area = 10 if self.garden else 0
        self.garden_orientation = "north" if self.garden else ""

    # Constrains
    @api.constrains("expected_price", "selling_price")
    def _check_price_difference(self):
        for prop in self:
            if (
                not float_is_zero(prop.selling_price, precision_rounding=0.01)
                and float_compare(prop.selling_price, prop.expected_price * 90.0 / 100.0, precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )


    # Actions
    def action_sold(self):
        if "canceled" in self.mapped("state"):
            raise UserError("Canceled properties cannot be sold.")
        return self.write({"state": "sold"})

    def action_cancel(self):
        if "sold" in self.mapped("state"):
            raise UserError("Sold properties cannot be canceled.")
        return self.write({"state": "canceled"})
    

    
