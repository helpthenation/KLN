openerp.disable_openerp_online = function(instance) {
    instance.web.WebClient.include({
        init: function(parent, client_options) {
            this._super(parent, client_options);
            this.set('title_part', {"zopenerp": " "});
        },
    });
};