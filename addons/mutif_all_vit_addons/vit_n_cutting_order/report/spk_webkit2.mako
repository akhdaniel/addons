<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>

	<!-- The objects variable is a list of browse_record objects from OpenERP. -->
	<!-- It contains all the documents in OpenERP that you wanted to generate this report for. -->
	<!-- We loop on it in order to be able to output the information for each document -->
    %for o in objects :

    <!-- We want to print this report out and send it to the partner, so -->
    <!-- We use the partner_id field on our object to set the translation language -->
    <%
    	if hasattr(o, 'user_id'):
    		setLang(o.user_id.lang)
    %>

    <!-- Now we write the name field of our object as the title -->
    <!-- You can access any field or function on the object like this -->
    <!-- Notice above we use the same syntax to output the css variable that was given to use by OpenERP? -->
    <h1>
        ${ o.name }
    </h1>

	<% 
	    # Let's define a function to get the day of the week with Python. 
	    # Notice the <% and %> to open and close Python code blocks...
	    # They can also be used for 1 liners (see setLang above)
	    import time

	    def get_day():
	    	return time.strftime("%A")
	    
	%>

	<!-- We call our function in the same way as we ouput parameters and it will simply print the result -->
	<div style="font-weight: bold">
		Happy ${ get_day() }!
	</div>

	<!-- We can even create variables inside Python code blocks and use them later -->
	<%
	from datetime import datetime
	time = datetime.now()
	%>

	<!-- Here, I use a similar syntax to the for loops to write an if statement -->
	%if time.hour > 18 and time.hour < 8:
		Shouldn't you be at home?!
	%else:
	    Keep up the good work! :)
	%endif

	<!-- Don't forget to close your loops! -->
	%endfor

</body>
</html>