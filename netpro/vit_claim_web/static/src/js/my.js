$my_inc = 1;
function addField(){
	var my_input =  "<div class='row'>";
		my_input += "<div class='col-md-4 col-sm-4'><label class='control-label'>Diagnosis "+$my_inc+"</label></div>";
		my_input += "<div class='col-md-4 col-sm-4'><input type='text' id='diagnosis_"+$my_inc+"' class='form-control' /><input name='diagnosis_"+$my_inc+"' type='hidden' id='diagnosisval_"+$my_inc+"' /></div>";
		my_input += "</div><br />";

	var my_btn = $('#button_add_diagnosis');
	$(my_input).insertBefore(my_btn);
	$my_inc++;
}