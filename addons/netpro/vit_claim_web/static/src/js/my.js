'use strict';
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


$(".harga_benefit").on('change', function(){
    var val = $(this).val();
    var bef_id = $(this).attr('benefitid');
    var det_id = $(this).attr('detailid');
    var mplan_id = $(this).attr('mplan');
    $.ajax({
        url: '/claim/check_excess/',
        type: "POST",
        data: JSON.stringify({
            'jsonrpc':'2.0', 
            'method':'call', 
            'params':{
                    'nilai': val, 
                    'benefit': bef_id, 
                    'mplanid': mplan_id,
                    }, 
            'id':null
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
            var obj = JSON.parse(data.result);
            if(obj.success){
                var exc_el = "<label>Accepted  : </label><input class='form-control' name='accept."+det_id+"' readonly='readonly' value='"+obj.accepted+"' />";
                    exc_el+= "<label>Excess    : </label><input class='form-control' name='excess."+det_id+"' readonly='readonly' value='"+obj.excess+"' />";
                var anakbuah = $("span[id='"+bef_id+"']");
                $(exc_el).insertBefore(anakbuah);
            }
        },
    });
});