$(function(){

	var td=twitdao();

	//follow
	$('.follow').live('click', function(e){
		var ths=$(this);
		var screen_name=ths.attr('data');
		td.follow(screen_name, function(){
			ths.attr('href','/a/unfollow/'+screen_name)
			ths.text('UnFollow');
			ths.removeClass('follow').addClass('unfollow');
		});
		e.preventDefault();return false;
	});

	$('.unfollow').live('click',function(e){
		var ths=$(this);
		var screen_name=ths.attr('data');
		td.unFollow(screen_name, function(){
			ths.attr('href','/a/follow/'+screen_name)
			ths.text('Follow');
			ths.removeClass('unfollow').addClass('follow');
		});
		e.preventDefault();return false;
	});

	//block
	$('.block').live('click',function(e){
		var ths=$(this);
		var screen_name=ths.attr('data');
		td.block(screen_name, function(){
			ths.attr('href','/a/unblock/'+screen_name)
			ths.text('UnBlock');
			ths.removeClass('block').addClass('unblock');
		});
		e.preventDefault();return false;
	});
	$('.unblock').live('click',function(e){
		var ths=$(this);
		var screen_name=ths.attr('data');
		td.unBlock(screen_name, function(){
			ths.attr('href','/a/block/'+screen_name)
			ths.text('Block');
			ths.removeClass('unblock').addClass('block');
			$('.reported')
				.removeClass('reported')
				.addClass('report')
				.text('Report spam')
				.attr('href','/a/report_spam/'+screen_name);
		});
		e.preventDefault();return false;
	});

	//report
	$('.report').live('click',function(e){
		var ths=$(this);
		var screen_name=ths.attr('data');
		td.report(screen_name, function(){
			ths.attr('href','#');
			$('.block')
				.attr('href','/a/unblock/'+screen_name)
				.text('UnBlock')
				.removeClass('block')
				.addClass('unblock');
			ths.text('Reported!');
			ths.removeClass('report').addClass('reported');
		});
		e.preventDefault();return false;
	});

});