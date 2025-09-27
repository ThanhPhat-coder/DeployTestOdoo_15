# education_management/models/enrollment.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EducationEnrollment(models.Model):
    _name = "education.enrollment"
    _description = "Enrollment"
    _inherit = ['mail.thread']
    _order = "create_date desc"

    student_id = fields.Many2one('education.student', string="Student", required=True, ondelete='cascade')
    course_id = fields.Many2one('education.course', string="Course", required=True, ondelete='cascade')
    enroll_date = fields.Date(string="Enrollment Date", default=fields.Date.context_today)
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('in_progress','In Progress'),('done','Done'),('cancel','Cancelled')], default='draft', tracking=True)
    grade = fields.Float(string="Grade")
    note = fields.Text(string="Note")

    _sql_constraints = [
        ('student_course_uniq', 'unique(student_id, course_id)', 'Student cannot be enrolled twice in same course.')
    ]

    def action_confirm(self):
        for rec in self:
            # capacity check
            taken = self.env['education.enrollment'].search_count([('course_id','=',rec.course_id.id),('state','in',('confirmed','in_progress'))])
            if rec.course_id.capacity and taken >= rec.course_id.capacity:
                raise ValidationError("Course capacity reached.")
            rec.state = 'confirmed'

    def action_start(self):
        self.state = 'in_progress'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'
