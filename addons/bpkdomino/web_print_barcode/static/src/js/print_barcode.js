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
                self.$el.find('.oe_sidebar').append(QWeb.render('xPrintBarcodeMain', {widget: self}));
                self.$el.find('.oe_to_local_barcode').on('click', self.on_print_to_local_barcode);
            }
        },

        on_print_to_local_barcode: function () {
            var view = this.getParent();
            //css
            //var barcode = $('.oe_form_text_content').text();
            
            //objek
            barcode = view.datarecord.barcode_data;

            console.log(barcode);
            //urlencode()//jsonp: > jika tidak json.stringify
            $.ajax("http://localhost/pproxy/print.php", {
                type: "POST",
                dataType: "json",
                jsonrpc: "2.0",
                data: JSON.stringify({
                    "barcode" : barcode
                    }),
                contentType: "application/json",
                success: function(data) {},
            });
        },
    });
};