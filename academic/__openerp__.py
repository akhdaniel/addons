{
	"name": "Academic Information System", 
	"version": "1.0", 
	"depends": ["base","board"], 
	"author": "Author Name", 
	"category": "Education", 
	"description": """\
this is my academic information system module
""",
	"data": ["menu.xml", 
		"course.xml", 
		"session.xml",
		"attendee.xml",
		"partner.xml",
		"workflow.xml",
		"security/group.xml",
		"security/ir.model.access.csv",
		#"wizard/create_attendee_view.xml"
		"report/session.xml",
		"dashboard.xml"
		],
	"installable": True,
	"auto_install": False,
}