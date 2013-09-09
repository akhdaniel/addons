{
    'name': 'ppi_training',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource - Training PT.PPI
""",    
    'depends': ['hr','hr_recruitment','hrd_ppi'],
    'update_xml':[
            'security/groups.xml',
            'security/ir.model.access.csv',
            'training_view.xml',
            'report/hr_training.xml',
            'action.xml',
            'training_workflow.xml',
            'tab_training.xml',
            ],
    'data': [],
    'installable':True,
}
