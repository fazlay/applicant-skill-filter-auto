# -*- coding: utf-8 -*-
{
   'name': "HR Skill Auto Filter",
 'summary': """Auto-filter applicants by skills and move to next stage""",
    'description': """
        - Adds skill selection to application forms
        - Auto-moves matching candidates to next stage
        - Filters non-matching applicants to initial stage
    """,
    'author': "Fazlay Rabbi",
    'website': "https://www.linkedin.com/in/fazlay0rabbi",
    'category': 'Human Resource',
    'version': '18.0.1.0',
    'icon': '/hr_skill_auto_filter/static/description/icon.png',

   'depends': ['hr_recruitment',"hr_recruitment_skills"],
        'assets': {
        'web.assets_frontend': [
            'hr_skill_auto_filter/static/lib/select2/js/select2.min.js',
            'hr_skill_auto_filter/static/lib/select2/css/select2.min.css',
            'hr_skill_auto_filter/static/src/js/portal_select2.js',
        ],
    },
    'data': [
        'views/portal_template.xml'
    ],
    

}

