from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PMKTCampaign(models.Model):
    _name = "pmkt.campaign"
    _description = "Marketing Campaign (Test Demo)"

    name = fields.Char(required=True)
    budget = fields.Monetary(default=0.0, currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )
    active = fields.Boolean(default=True)

    @api.constrains('budget')
    def _check_budget_non_negative(self):
        for rec in self:
            if rec.budget < 0:
                raise ValidationError("Budget phải >= 0")
