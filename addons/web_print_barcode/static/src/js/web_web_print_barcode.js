//#############################################################################
//  @@@ web_print_barcode custom JS @@@
//#############################################################################
openerp.web_print_barcode = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function () {
            var self = this,
                view = this.getParent();
            this._super.apply(this, arguments);
            console.log(view);
            if ((view.model == 'material.requirement') && (self.getParent().ViewManager.active_view == 'form')) {
                self.$el.find('.oe_sidebar').append(QWeb.render('vitPrintBarcodeMain', {widget: self}));
                self.$el.find('.oe_to_local_barcode').on('click', self.on_print_to_local_barcode);
            }
        },

        on_print_to_local_barcode: function () {
            console.log("function ok");
            var barcode = document.getElementById("name");//barcode_command
            //urlencode()
            //var countryID = e.options[e.selectedIndex].value;
            //jsonp:
            console.log(barcode);
            $.ajax("http://localhost", {
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    "barcode" : barcode
                }),
                success: function(data) {
                    // var res = '<option value="">- Choose State -</option>';
                    // $.each(JSON.parse(data.result), function(key,val) {
                    //     res += '<option value="'+ key +'">'+ val+'</option>';
                    // });

                    //replace exiting html in state with this one
                    // $('#state_id').html(res);           
                    // },
                },
                contentType: "application/json",
                ); 
            }
    });

};
