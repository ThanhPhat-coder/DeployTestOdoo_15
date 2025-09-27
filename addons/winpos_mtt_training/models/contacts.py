from odoo import models, fields


class Contact(models.Model):
    _name = "winpos_mtt_training.contact"
    _description = "Contact"

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    age = fields.Integer(string='Age')

    def is_adult(self):
        if self.age:
            return self.age >= 18
        return False

    def contact_info(self):
        email = self.email if self.email else 'N/A'
        phone = self.phone if self.phone else 'N/A'
        return f"{self.name} - {email} - {phone}"
