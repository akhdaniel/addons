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
            var view = this.getParent();
            //jika pakai css
            //var barcode = $('.oe_form_text_content').text();
            
            //jika pakai objek
            var barcode = view.datarecord.barcode_data;

            console.log(barcode);
            //urlencode()//jsonp: > jika tidak json.stringify
            $.ajax("http://localhost", {
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    "barcode" : barcode
                    }),
                contentType: "application/json",
                success: function(data) {},
            });
        },
    });
};