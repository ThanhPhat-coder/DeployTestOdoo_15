# education_management/__manifest__.py
{
    "name": "Education Management",
    "version": "1.0.0",
    "summary": "Basic education management: students, courses, enrollments",
    "description": "Module for managing students, courses and enrollments for education projects / thesis.",
    "author": "Your Name",
    "category": "Education",
    "depends": ["base", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/student_views.xml",
        "views/course_views.xml",
        "views/enrollment_views.xml",
        "views/education_menus.xml",
        'data/education_sequence.xml',
        "data/education_demo.xml",  
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
