//#############################################################################
//  @@@ web_print_printer_data custom JS @@@
//#############################################################################
openerp.vit_direct_print = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function () {
            var self = this,
                view = this.getParent();
            this._super.apply(this, arguments);
            if ((view.model == 'purchase.order') && (view.view_type == 'form') ) {
                console.log("objek ");
                self.$el.find('.oe_sidebar').append(QWeb.render('xPrintDirectMain', {widget: self}));
                self.$el.find('.oe_to_local_printer_data').on('click', self.on_print_to_local_printer_data);
            }
        },

        on_print_to_local_printer_data: function () {
            var view = this.getParent();

            printer_data = view.datarecord.printer_data;
            if (!printer_data){
                alert('No data to print. Please click Update Printer Data');
                return;
            }

            console.log(printer_data);
            //urlencode()//jsonp: > jika tidak json.stringify
            $.ajax("http://localhost/pproxy/print.php", {
                type: "POST",
                dataType: "json",
                jsonrpc: "2.0",
                data: JSON.stringify({
                    "printer_data" : printer_data
                    }),
                contentType: "application/json",
                success: function(data) {},
            });
        },
    });
};