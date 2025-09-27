# education_management/models/student.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EducationStudent(models.Model):
    _name = "education.student"
    _description = "Student"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name"

    name = fields.Char(string="Full Name", required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string="Contact")
    student_id = fields.Char(string="Student ID", required=True, copy=False, readonly=True,
                             default=lambda self: self.env['ir.sequence'].next_by_code('education.student') if self.env['ir.sequence'].search([('code','=','education.student')]) else None)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    birthdate = fields.Date(string="Birthdate")
    gender = fields.Selection([('male','Male'),('female','Female'),('other','Other')], string="Gender")
    enroll_ids = fields.One2many('education.enrollment', 'student_id', string="Enrollments")
    active = fields.Boolean(default=True)

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError("Invalid email for student %s" % rec.name)
