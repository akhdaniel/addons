{
    'name': 'Vitraining.com / Training',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource - Training
""",    
    'depends': ['hr','hr_recruitment','hrd_employee'],
    'update_xml':[
            'training_view.xml',
            'report/hr_training.xml',
            'action.xml',
            'training_workflow.xml',
            #'tab_training.xml',
            'master_training.xml',
            ],
    'data': [],
    'installable':True,
}
