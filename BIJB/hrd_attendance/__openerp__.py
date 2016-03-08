{
    'name': 'HRD Attendance',
    'author'  :'vitraining.com',
    'category': 'Human Resources',
    'description': """
Import tool untuk kehadiran karyawan dari data fingerprint berdasarkan
Fingerprint ID karyawan
""",    
    'depends': ['hr_attendance','hrd_employee'],
    'update_xml':[
        'hrd_attendance.xml'],
    'data': [],
    'installable':True,
}
