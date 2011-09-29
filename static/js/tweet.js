$(function(){

	var td=twitdao();

	//update
	function updateStatus(){
		var in_reply_to_status_id = $('#In_reply_to_status_id').val();
		var status = $('#Status').val();
		var lat=$('#TweetForm input[name=lat]').val();
		var l0ng=$('#TweetForm input[name=long]').val();
		var others=(lat&&l0ng)?{'lat':lat,'long':l0ng}:{};
		$('#TweetButton').attr('disabled','disabled');
		td.update(status,in_reply_to_status_id,others,function(d){
			$('#TweetButton').removeAttr('disabled');
			$('#In_reply_to_status_id').val('');
			$('#Status').val('');
			if(getConfig('tsn')==getConfig('osn')){
				$('#TweetsCount').text(Number($('#TweetsCount').text())+1);
			}
			$("#UploadArea").fadeOut(function(){
				$("#UploadMedia").show();
				$("#UploadMask").hide();
				$("#UploadPreview").html('').hide();
			});
			charLeft();
		},function(){
			$('#TweetButton').removeAttr('disabled');
		});
	}
	$('#TweetButton').click(function(e){
		updateStatus();
		e.preventDefault();return false;
	});
	$("#Status")
	.change(function(){charLeft();changeHeading();})
	.keydown(function(){charLeft();changeHeading();})
	.keyup(function(){charLeft();changeHeading();})
	.keydown(function(event){
		if(event.ctrlKey && event.keyCode==13){updateStatus();}
	});

	//upload
	$('#UploadButton').click(function(){
		$('#UploadArea').slideToggle('fast');
	});
	$('#IUpload').load(function(){
		var i = $(this)[0], d, data;
		if (i.contentDocument){d = i.contentDocument;}
		else if(i.contentWindow){d = i.contentWindow.document;}
		else{d = window.frames['IUpload'].document;}
		if(d.location.href == "about:blank") {return;}
		data=$.parseJSON(d.body.innerHTML);
		if(data && data.success)
		{
			var l=' '+data['response']['url'],o=$('#Status').val();
			var s=$('#Status').val(o+l)[0];
			setCursorPos(s, o.length);
			$('#UploadMask').hide();
			$('#UploadPreview').html('<img src="/i/twitpic/thumb/'+data['response']['id']+'" />').fadeIn();
		}else{
			errorEndTip('Fail!');
			$("#UploadMedia").show();
			$("#UploadMask").hide();
			$("#UploadPreview").hide();//
		}
		try{$('#UploadForm')[0].reset()}
		catch(e){$('#UploadForm').val('')}
	});
	$('#UploadFile').change(function(e){
		if($('#UploadFile').val()=='')return;
		$("#UploadMask").show();
		$("#UploadMedia").hide();
		$('#UploadForm').submit();
	});
	$('#UploadCancel').click(function(){
		$("#UploadArea").hide();
		$("#UploadMedia").show();
		$("#UploadMask").hide();
		$("#UploadPreview").html('').hide();
	});
	
	//delete
	$('.tweet .delete').live('click',function(e){
		var ths=$(this);
		var id=ths.closest('.tweet').attr('tid');
		td.del(id,function(){
			ths.closest('.tweet').remove();
			if(getConfig('tsn')==getConfig('osn')){
				$('#TweetsCount').text(Number($('#TweetsCount').text())-1);
			}
		});
		e.preventDefault();return false;
	});

	//show
	$('.tweet .show-reply-to').live('click',function(e){
		var ths=$(this);
		var id=ths.closest('.tweet').attr('rid');
		var quotex=ths.closest('.tweet').find('.reply-to');
		if(quotex.html()==''){
			td.show(id, function(d){
				quotex.append(d.tweet);
			});
		}
		e.preventDefault();return false;
	});

	//favorite
	$('.tweet .fav').live('click', function(e){
		var ths = $(this);
		var sid=ths.closest('.tweet').attr('sid');
		var tid =ths.closest('.tweet').attr('tid');
		var id=sid?sid:tid;
		td.favorite(id,function(){
			ths.removeClass('fav').addClass('unfav').text('★Favorite');
			ths.closest('.tweet').addClass('favorited');
		},function(){
			ths.text('☆Favorite');
		});
		e.preventDefault();return false;
	});
	//unFavorite
	$('.tweet .unfav').live('click', function(e){
		var ths = $(this);
		var sid=ths.closest('.tweet').attr('sid');
		var tid =ths.closest('.tweet').attr('tid');
		var id=sid?sid:tid;
		td.unFavorite(id,function(){
			ths.removeClass('unfav').addClass('fav').text('☆Favorite');
			ths.closest('.tweet').removeClass('favorited');
		},function(){
			ths.text('★Favorite');
		});
		e.preventDefault();return false;
	});

	//retweet
	var active=false;
	$('.retweet').live('click',function(e){
		var ths=$(this);
		var sid=ths.closest('.tweet').attr('sid');
		var tid =ths.closest('.tweet').attr('tid');
		var id=sid?sid:tid;
		td.retweet(id,function(d){
			ths.text('Undo Retweet');
			ths.closest('.tweet').attr('uid', d.tweet.id_str).addClass('retweeted');
			ths.removeClass('retweet').addClass('unrt');
			if(getConfig('tsn')==getConfig('osn')){
				$('#TweetsCount').text(Number($('#TweetsCount').text())+1);
			}
		});
		e.preventDefault();return false;
	});

	//undo retweet
	var active=false;
	$('.unrt').live('click',function(e){
		var ths=$(this);
		var id=ths.closest('.tweet').attr('uid');
		td.undoRetweet(id, function(){
			ths.text('Retweet');
			ths.closest('.tweet').removeAttr('uid').removeClass('retweeted');
			ths.removeClass('unrt').addClass('retweet');
			if(getConfig('tsn')==getConfig('osn')){
				$('#TweetsCount').text(Number($('#TweetsCount').text())-1);
			}
		});
		e.preventDefault();return false;
	});

	//quote
	$('.quote').live('click', function(e){
		var name = $(this).closest('.tweet').children('.tweet-body').find('.tweet-heading .screen_name').text();
		var text = $(this).closest('.tweet').children('.tweet-body').find('.tweet-text').text();
		$('#TweetForm').show();
		var s=$('#Status').val('RT @'+name+': '+text).focus()[0];
		setCursorPos(s,0);charLeft();
		e.preventDefault();return false;
	});

	//reply
	$('.reply').live('click', function(e){
		var ths=$(this);
		var name=ths.closest('.tweet').children('.tweet-body').find('.tweet-heading .screen_name').text();
		var sid =ths.closest('.tweet').attr('sid');
		var tid =ths.closest('.tweet').attr('tid');
		var id=sid?sid:tid;
		var text=$(this).closest('.tweet').children('.tweet-body').find('.tweet-text').text();
		
		var to='@'+name;
		var at='',aa={};
		if( (m=text.match(/@[\w\d_]+/g))!=null ){
			for(var i=0;i<m.length;i++){
				aa[m[i]]=m[i];
			}
			delete aa[to];
			delete aa['@'+getConfig('tsn','')]
		}
		for(var a in aa){at+=(a+' ');}
		$('#TweetForm').show();
		$('#In_reply_to_status_id').val(id);
		var s = $('#Status').focus().val(to+' '+at)[0];
		setSelectionRange(s, to.length+1, (to+' '+at).length);
		changeHeading();charLeft();
		e.preventDefault();return false;
	});

	//geo
	$('.show-geo').live('click', function(e){
		$(this).closest('.tweet').children('.tweet-body').find('.media-preview .geo').slideToggle();
		e.stopPropagation();e.preventDefault();
	});

	//tweet common actions
	$('.tweet').live('mouseover', function(){
		$(this).addClass('over').children('.tweet-body').find('.tweet-bottom .tweet-action').show().css('display','block');
	}).live('mouseout',function(){
		$(this).removeClass('over').children('.tweet-body').find('.tweet-bottom .tweet-action').hide();
	});

	var saved_tweet=getCookie('saved_tweet');
	$('#Status').val(saved_tweet==null?'':saved_tweet);
	changeHeading();charLeft();

});