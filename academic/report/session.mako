<html>
<head>
<style type="text/css">${css}</style> </head>
<body>
	<h1>Session Report</h1>
	% for session in objects:
		<h2>${session.course_id.name} - ${session.name}</h2>
		<p>From ${formatLang(session.start_date, date=True)}.</p>
		<p>Attendees:
			<ul>
				% for att in session.attendee_ids: 
				<li>${att.partner_id.name}</li>
				% endfor
			</ul> 
		</p>
	% endfor
</body>
</html>