{
    'name': 'HR AI Bot',
    'version': '1.1',
    'category': 'HR',
    'summary': 'AI HR assistant using Discuss + RAG',
    'depends': ['mail', 'documents'],
    'external_dependencies': {
        'python': ['litellm'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/hr_ai_config_views.xml',
        'views/hr_ai_document_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'application': True,
    'installable': True,
}
