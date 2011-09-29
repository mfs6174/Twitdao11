$(function(){

	var td=twitdao();

	//message-reply
	$('.reply-msg').live('click',function(e){
		var name = $(this).closest('.message').attr('rname');
		$('#SendTo').val(name);
		$('#MessageForm textarea').focus();
		e.preventDefault();return false;
	});

	//message-send
	function sendMessage(){
		$('#Send').attr('disabled','disabled');
		var ths=$('#MessageForm');
		var text=ths.find('textarea').val();
		var screen_name=$('#SendTo').val();
		td.send(text, screen_name, function(){
			$('#Send').removeAttr('disabled');
			$('#SendTo').val('');
			ths.find('textarea').val('');
		},function(){
			$('#Send').removeAttr('disabled');
		})
	}
	$('#MessageForm form').submit(function(e){
		sendMessage();
		e.preventDefault();return false;
	});
	$("#MessageForm textarea").keydown(function(e){
		if(e.ctrlKey && e.keyCode==13){sendMessage();}
	});
	
	//message-delete
	$('.delete-msg').live('click', function(e){
		var msg=$(this).closest('.message')
		var id=msg.attr('mid');
		td.delmsg(id,function(){
			msg.remove();
		});
		e.preventDefault();return false;
	});

});