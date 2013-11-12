{
    'name': 'HR PPI / Training',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource - Training PT.PPI
""",    
    'depends': ['hr','hr_recruitment','hrd_ppi'],
    'update_xml':[
            'security/ir.model.access.csv',
            'training_view.xml',
            'report/hr_training.xml',
            'action.xml',
            'training_workflow.xml',
            'tab_training.xml',
            'master_training.xml',
            ],
    'data': [],
    'installable':True,
}
