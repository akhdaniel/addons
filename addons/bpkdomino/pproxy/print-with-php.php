<head>
<script src="//code.jquery.com/jquery-1.11.3.min.js"></script>    
</head>

<body>
<button id="print" name="print">Print Test</button>

<script>
$(document).ready(function(){
    $("#print").click(function(){
        var barcode = "ini dua kali";
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