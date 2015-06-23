<head>
<script src="//code.jquery.com/jquery-1.11.3.min.js"></script>    
</head>

<body>
<button id="print" name="print">Print Test</button>

<script>
$(document).ready(function(){
    $("#print").click(function(){
        var barcode = 'N\nA1,0,0,1,1,1,N,"Buku A4"\nB1,10,0,E30,2,2,40,B,"0123012340008"\nP' ;
        barcode = encodeURIComponent(barcode);
        
        $.ajax("http://127.0.0.1/pproxy/print.php", {
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
                "barcode" : barcode
                }),
            contentType: "application/json",
            success: function(data) {
                console.log(data);
            },
        });
    });
}); 
</script>

</body>