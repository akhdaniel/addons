openerp.xport_xcel = function(instance, m) {
    
    var _t = instance.web._t,
    QWeb = instance.web.qweb;
    
    instance.web.FormView.include({
        load_form: function(data) {
            var self = this;
            this._super.apply(this, arguments);
            self.$el.find('.oe_xdates').append(QWeb.render('xportxcel', {widget: self}));
            self.$el.find('.oe_xport').unbind('click').click(function(event){self.on_xport_excel("excel")})
        },

        on_xport_excel: function (export_type) {
            var self = this
            var view = this.getParent()
            dates=[]
            header_list=[]
        	datefrom 	= self.$el.find('.oe_dt_from > span > input')
            $from = $(datefrom).datepicker( "getDate" )
            datefrom = $from.getFullYear() + "-" + ($from.getMonth()+1) + "-" + $from.getDate()
        	
        	dateto 		= self.$el.find('.oe_dt_to > span > input')
            $to = $(dateto).datepicker( "getDate" )
            dateto = $to.getFullYear() + "-" + ($to.getMonth()+1) + "-" + $to.getDate()
        	
        	/*datetrf 	= self.$el.find('.oe_dt_trf > span > input')
            $trf = $(datetrf).datepicker( "getDate" )
            datetrf = $trf.getFullYear() + "-" + ($trf.getMonth()+1) + "-" + $trf.getDate()*/

            dates.push({'datefrom':datefrom,'dateto':dateto})
        	header_list.push({'data': ['Nama','Jabatan/direktorat','Total','Bank','No. Rekening','Cabang']})
            var str2 = new Date().toJSON().slice(0,10)
            var models = 'Transfer_per_'.concat(str2).concat('.xls')

        	//Export to excel
            $.blockUI();
            //if (export_type === 'excel'){
                view.session.get_file({
                    url: '/xport_xcel/xport_xcel',
                    data: {data: JSON.stringify({
                            model :models,
                            headers : header_list,
                            rows : dates,
                    })},
                    complete: $.unblockUI
                });
            //}
        },
    });
};