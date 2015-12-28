{
    'name': 'hrd_ppi',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Human Resource PT.PPI
""",    
    'depends': ['hr','hr_recruitment','hr_payroll','hr_attendance','hrd_ppi_payroll','base_import'],
    'update_xml':[
            'security/groups.xml',
            'security/ir.model.access.csv',
            'action.xml',
            'hr_recruitment.xml',
            'hr_applicant_view.xml',           
            'hr_employs_tab.xml',  
            'grade_structure.xml',   
            'title_structure.xml',
    	    'title_view.xml',
        	'payslip_view.xml', 
			'extitle.xml',
            'hr_applicant_view.xml',
            'hr_contract_view.xml',
            'wizard/recruitment_wizard_view.xml',
            'warning_view.xml',
            'contract_structure.xml',
            'report/report_recruitmen.xml',
            'report/employee_info.xml'
            ],
    'data': [],
    'installable':True,
}
