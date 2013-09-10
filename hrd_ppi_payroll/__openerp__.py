{
    'name': 'hrd_ppi_payroll',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Hitung Lembur, Payroll, dan PPH21 
Human Resource PT.PPI
""",    
    'depends': ['hr','hr_recruitment','hr_attendance',"hr_payroll"],
    'update_xml':[
    	'salary_structure.xml',
    	'report/hr_payrport.xml',
  	
    ],
    'data': [],
    'installable':True,
}
