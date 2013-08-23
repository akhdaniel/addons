{
    'name': 'ppi',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource PT.PPI
""",    
    'depends': ['hr','hr_recruitment'],
    'update_xml':[
            'security/groups.xml',
            'training_view.xml',
            'action.xml',
            'hr_recrutment.xml',
            'hr_applicant_view.xml',           
            'tab_training.xml',
            'ppi_workflow.xml',
            ],
    'data': [],
    'installable':True,
}
