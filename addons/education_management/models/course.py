# education_management/models/course.py
from odoo import models, fields, api

class EducationCourse(models.Model):
    _name = "education.course"
    _description = "Course"
    _order = "name"

    name = fields.Char(string="Course Name", required=True)
    code = fields.Char(string="Course Code", required=True)
    description = fields.Text(string="Description")
    credits = fields.Float(string="Credits", default=3.0)
    capacity = fields.Integer(string="Capacity", default=30)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    instructor_id = fields.Many2one('res.users', string="Instructor")
    enroll_ids = fields.One2many('education.enrollment', 'course_id', string="Enrollments")

    def seats_available(self):
        for rec in self:
            used = len(rec.enroll_ids.filtered(lambda r: r.state in ('confirmed','in_progress')))
            rec.seats_left = max(0, rec.capacity - used)

    seats_left = fields.Integer(string="Seats Left", compute="seats_available", store=False)
