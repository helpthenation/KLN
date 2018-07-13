openerp.petstore = function(instance, local) {

    instance.web.form.widgets = instance.web.form.widgets.extend(
	{
		'test' : 'instance.web.form.message',
	});

    instance.web.form.message = instance.web.form.FieldChar.extend(
	{
        template: 'test',
        start: function() {
        var self=this;
      	$('button#message').click(this.show_message);
       },
       
       show_message :function(){
        alert("First Message");
       }
});
}

