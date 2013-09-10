{
    'name': 'hrd_ppi',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource PT.PPI
""",    
    'depends': ['hr','hr_recruitment','hr_payroll','hr_attendance','hrd_ppi_payroll'],
    'update_xml':[
            'security/groups.xml',
            'security/ir.model.access.csv',
            'action.xml',
            'hr_recruitment.xml',
            'hr_applicant_view.xml',           
            'ppi_workflow.xml',
            'hr_employs_tab.xml',  
            'grade_structure.xml',   
            'title_structure.xml',
    	    'title_view.xml',
        	'payslip_view.xml'      
            ],
    'data': [],
    'installable':True,
}
