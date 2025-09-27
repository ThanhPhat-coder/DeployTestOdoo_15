{
    "name": "WINPOS MTT Training",
    "version": "15.0.1.0.0",
    "license": "LGPL-3",
    "summary": "Ví dụ module cho tests: ERP (Sale) và PMKT (Campaign)",
    "depends": ["base", "web", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/pmkt_campaign_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.qunit_suite_tests": [
            "winpos2_mtt_training/static/tests/*.js",
        ],
    },
    "installable": True,
    "application": True,
}
