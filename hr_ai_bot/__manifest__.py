{
    'name': 'HR AI Bot (POC)',
    'version': '1.0',
    'category': 'HR',
    'summary': 'AI HR assistant using Discuss + RAG',
    'depends': ['mail', 'mail', 'documents'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_ai_config_views.xml',
        'views/hr_ai_document_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'application': True,
    'installable': True,
}
