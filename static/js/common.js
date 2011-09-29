function getConfig(name, defval){
	if(typeof $c!='undefined'){
		return $c[name];
	}
	return defval;
}

function charLeft(num) {
	if(!num)num=140;
	var tweet=$("#Status").val();
	if(tweet==null||typeof tweet.length=='undefined')return;
	var left=num-tweet.length;
	if(left<0){$("#CharCounter").css("color","#C00");}
	else{$("#CharCounter").css("color","#000");}
	$("#CharCounter").html(left);
	setCookie('saved_tweet',tweet.substr(0,280),3600*24*30);
}

function changeHeading(){
	var text=$('#Status').val();
	if(text==null||typeof text.match=='undefined')return;
	if((m=text.match(/^@([\w\d_]+).*/))!=null){
		$('#TweetForm h3').text('Reply to '+m[1]);
	}else{
		$('#In_reply_to_status_id').val('');
		$('#TweetForm h3').text('What\'s happening?');
	}
}

function updateDate(){
	$(".created-at").each(function(){
		var date = new Date(Number($(this).attr("time"))),
			now = new Date(),
			differ = (now - date)/1000,
			dateFormated = '';
		
		if(differ <= 0){
			dateFormated='Just now!';
		}else if(differ < 60){
			dateFormated = Math.ceil(differ) + " seconds ago";
		}else if(differ < 3600){
			dateFormated = Math.ceil(differ/60) + " minutes ago";
		}else if(differ < 3600*24){
			dateFormated = "about " + Math.ceil(differ/3600) + " hours ago";
		}/*else if(differ < 3600*24*7){
			dateFormated = "about " + Math.floor(differ/3600/24) + " days ago";
		}*/else{
			dateFormated = date.toLocaleString();
		}
		$(this).text(dateFormated);
	});
}

function startTip(text){
	$('#Tip').text(text).fadeIn('fast');
}
function endTip(text){
	$('#Tip').text(text).fadeIn('fast');
	setTimeout(function(){
		$('#Tip').fadeOut();
	},1500);
}
function errorEndTip(text){
	$('#Tip').text(text).fadeIn('fast').addClass('error');
	setTimeout(function(){
		$('#Tip').fadeOut(function(){
			$(this).removeClass('error');
		});
	},1500);
}

function startTinyTip(text){
	$('#TinyTip').text(text).show();
}
function endTinyTip(text){
	if(text){
		$('#TinyTip').text(text).fadeOut();
	}else{
		$('#TinyTip').fadeOut();
	}
}

function setCookie(name, value, seconds) {
	value=encodeURIComponent(value);
	if (typeof(seconds) != 'undefined') {
		var date = new Date();
		date.setTime(date.getTime() + (seconds*1000));
		var expires = "; expires=" + date.toGMTString();
	}else{
		var expires = "";
	}
	document.cookie = name+"="+value+expires+"; path=/";
}
function getCookie(name) {
	name = name + "=";
	var carray = document.cookie.split(';');
	for(var i=0;i < carray.length;i++) {
		var c = carray[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(name) == 0) return decodeURIComponent(c.substring(name.length,c.length));
	}
	return null;
}
function deleteCookie(name) {
	setCookie(name, "", -1);
}



function setSelectionRange(input, startIndex, stopIndex){
	if (input.setSelectionRange){
		input.setSelectionRange(startIndex, stopIndex);
		input.focus();
	}else if(input.createTextRange){//IE
		var range = input.createTextRange();
		range.collapse(true);
		range.moveStart('character', startIndex);
		range.moveEnd('character', stopIndex - startIndex);
		range.select();
	}
}
function setCursorPos(input, pos){
	setSelectionRange(input, pos, pos);
}

function twitdao(){
	var _={};
	_.del_active=false;
	_.fav_active=false;
	_.ret_active=false;
	_.upd_active=false;
	_.fol_active=false;
	_.blk_active=false;
	_.rep_active=false;
	_.shw_active=false;
	_.sed_active=false;//message
	_.del=function(id, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		if(!confirm('Are you sure you want to delete this tweet?'))return;
		startTip('Deleting...');
		if(!t.del_active){
			t.del_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/delete/'+id,
				'dataType':'json',
				'success':function(d){
					t.del_active=false;
					if(d&&d.success){
						endTip('Tweet deleted!');
						success(d);
					}else if(d&&d.info){
						error(d);
						errorEndTip(d.info);
					}else{
						error(d);
						errorEndTip('Oops! Unknown Error!');
					}
				},
				'error':function(){t.del_active=false;error();}
			});
		}
	};
	_.show=function(id, success, error, start, end){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTinyTip('Loading...');
		if(!t.shw_active){
			t.shw_active=true;
			$.ajax({
				'type':"GET",
				'url':'/x/show/'+id,
				'dataType':'json',
				'success':function(d){
					t.shw_active=false;
					if(d&&d.success){
						endTinyTip('Ok!');
						success(d);
					}else if(d&&d.info){
						error(d);
						endTinyTip(d.info);
					}else{
						error(d);
						endTinyTip('Oops! Unknown Error!');
					}
				},
				'error':function(){t.shw_active=false;error();}
			});
		}
	};
	_.retweet=function(id,success,error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTip('Retweeting...');
		if(!t.ret_active){
			t.ret_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/retweet/'+id,
				'dataType':'json',
				'success':function(d){
					t.ret_active=false;
					if(d&&d.success){
						endTip('Retweeted!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Unknown Error!');
						error(d);
					}
				},
				'error':function(){t.ret_active=false;error();}
			});
		}
	};
	_.undoRetweet=function(id, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTip('Trying to undo Retweet...');
		if(!t.ret_active){
			t.ret_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/delete/'+id,
				'dataType':'json',
				'success':function(d){
					t.ret_active=false;
					if(d&&d.success){
						endTip('Success!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Unknown Error!');
						error(d);
					}
				},
				'error':function(){t.ret_active=false;error();}
			});
		}
	};
	_.favorite=function(id, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTip('Trying to add favorite tweet...');
		if(!t.fav_active){
			t.fav_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/favorite/'+id+'/create',
				'dataType':'json',
				'success':function(d){
					t.fav_active=false;
					if(d&&d.success){
						endTip('Favorited!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Something going wrong.');
						error(d);
					}
				},
				'error':function(){t.fav_active=false;error();}
			});
		}
	};
	_.unFavorite=function(id,success,error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTip('Trying to delete favorite tweet...');
		if(!t.fav_active){
			t.fav_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/favorite/'+id+'/delete',
				'dataType':'json',
				'success':function(d){
					t.fav_active=false;
					if(d&&d.success){
						endTip('UnFavorited!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Something going wrong.');
						error(d);
					}
				},
				'error':function(){t.fav_active=false;error();}
			});
		}
	};
	_.update=function(status, in_reply_to_status_id, others, success, error){
		var isf=$.isFunction(others);
		error=isf?success:error;
		success=isf?others:success;
		others=isf?{}:others;
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		if(status.length>140){
			errorEndTip('Status is over 140 characters.');
			error();
			return;
		};
		startTip('Updating status...');
			if(!t.upd_active){
			t.upd_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/update',
				'dataType':'json',
				'data':$.extend({'in_reply_to_status_id':in_reply_to_status_id, 'status':status}, others),
				'success':function(d){
					t.upd_active=false;
					if(d&&d.success){
						charLeft();
						endTip('Status updated successfully!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Unknown Error!');
						error(d);
					}
				},
				'error':function(){
					t.upd_active=false;
					error();
				}
			});
		}
	};
	_.follow=function(screen_name, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTip('Trying to Follow '+ screen_name +' ...');
		if(!t.fol_active){
			t.fol_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/friends/'+screen_name+'/make',
				'dataType':'json',
				'success':function(d){
					t.fol_active=false;
					if(d&&d.success){
						endTip(screen_name+' is your friend now!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Something going wrong.');
						error(d);
					}
				},
				'error':function(){t.fol_active=false;error();}
			});
		}
	};
	_.unFollow=function(screen_name, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTip('Trying to unfollow '+screen_name+'...');
		if(!t.fol_active){
			t.fol_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/friends/'+screen_name+'/break',
				'dataType':'json',
				'success':function(d){
					t.fol_active=false;
					if(d&&d.success){
						endTip(screen_name+' is not your friend anymore.');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Something going wrong.');
						error(d);
					}
				},
				'error':function(){t.fol_active=false;error();}
			});
		}
	};
	_.block=function(screen_name, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTip('Trying to block '+screen_name+' ...');
		if(!t.blk_active){
			t.blk_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/block/'+screen_name+'/add',
				'dataType':'json',
				'success':function(d){
					t.blk_active=false;
					if(d&&d.success){
						endTip(screen_name+' is blocked!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Something going wrong.');
						error(d);
					}
				},
				'error':function(){t.blk_active=false;error();}
			});
		}
	};
	_.unBlock=function(screen_name, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		startTip('Trying to unblock ' +screen_name+ ' ...');
		if(!t.blk_active){
			t.blk_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/block/'+screen_name+'/remove',
				'dataType':'json',
				'success':function(d){
					t.blk_active=false;
					if(d&&d.success){
						endTip(screen_name+' is unblocked!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Something going wrong.');
						error(d);
					}
				},
				'error':function(){t.blk_active=false;error();}
			});
		}
	};
	_.report=function(screen_name, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		if(!confirm('Will report '+screen_name+' for spam.\n Are you sure?'))return;
		startTip('Trying to report ' +screen_name+ ' for spam ...');
		if(!t.rep_active){
			t.rep_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/report/'+screen_name,
				'dataType':'json',
				'success':function(d){
					t.rep_active=false;
					if(d&&d.success){
						endTip(screen_name+' is reported and blocked!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Something going wrong.');
						error(d);
					}
				},
				'error':function(){t.rep_active=false;error();}
			});
		}
	};
	_.send=function(text, screen_name, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		if(text.length>140){
			errorEndTip('Message is over 140 characters.');
			error();
			return;
		}else if(text&&text.length<=0){
			errorEndTip('Message is empty.');
			error();
			return;
		};
		startTip('Sending message...');
		if(!t.sed_active){
			t.sed_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/message_send',
				'dataType':'json',
				'data':{'screen_name':screen_name, 'text':text},
				'success':function(d){
					t.sed_active=false;
					if(d&&d.success){
						endTip('Message sent!');
						success(d);
					}else if(d&&d.info){
						errorEndTip(d.info);
						error(d);
					}else{
						errorEndTip('Oops! Unknown Error!');
						error(d);
					}
				},
				'error':function(){
					t.sed_active=false;
					error();
				}
			});
		}
	};

	_.dms_active=false;
	_.delmsg=function(id, success, error){
		if(!$.isFunction(success))success=function(){}
		if(!$.isFunction(error))error=function(){}
		var t=this;
		if(!confirm('Are you sure you want to delete this Message?'))return;
		startTip('Deleting...');
		if(!t.dms_active){
			t.dms_active=true;
			$.ajax({
				'type':"POST",
				'url':'/x/message_destroy/'+id,
				'dataType':'json',
				'success':function(d){
					t.dms_active=false;
					if(d&&d.success){
						endTip('Message deleted!');
						success(d);
					}else if(d&&d.info){
						error(d);
						errorEndTip(d.info);
					}else{
						error(d);
						errorEndTip('Oops! Unknown Error!');
					}
				},
				'error':function(){t.dms_active=false;error();}
			});
		}
	};
	return _;
}

function more(more_url, params){
	var _={};
	_.url=more_url;
	_.params=params;
	_.active=false;
	_.count=0;
	_.do_more=function(callback){
		var current=document.location.pathname;
		var t=this;
		$('#pagination .loading').show();
		$('#pagination .more').hide();
		$.ajax({
			'type':"GET",
			'url':t.url,
			'data':t.params,
			'dataType':'json',
			'success':function(d){
				if(d&&d.success){
					$('#pagination .loading').hide();
					if(d.count<=0){return;}
					$('#Timeline .tweets').append(d.tweets);
					$('#pagination .more').attr('href',d.href||'').show();
					t.params=d.params;
				}
				updateDate();
				callback(d);
			},
			'error':function(){
				$('#pagination .more').show();
				$('#pagination .loading').hide();
				callback();
			}
		});
	};
	_.next=function(){
		var t=this;
		if(!t.active){
			t.active=true;
			t.do_more(function(){
				t.active=false;
				t.count++;
			});
		}
	};
	$(function(){
		$('#pagination .more').live('click', function(e){
			_.next();e.preventDefault();
		});
		var max_more=100, preload=50+50;
		$(window).bind('scroll',function(){
			if( _.count<max_more && ($('body').height()-preload) < ($(window).height()+$(window).scrollTop()) ){
				_.next();
			}else if($('#Timeline .tweets').length>this.page_size){
				_.collapse();
			}
		});
	});
	return _;
}

function refresh(url, params){

	var live_initial=3000; //恢复时间
	var live_interval=5000; //显示间隔时间

	var interval=5000;
	var min_interval=3000; //最短刷新时(暂定)
	var max_interval = 60*1000; //最长刷新间隔(暂定)
	var decay=1.5; //刷新间隔调整系数(暂定)

	var counter=0;//for logging.
	var otitle=document.title;

	var console=window.console||{log:function(){}};
	//console={log:function(){}};

	var live={
		timer:null,
		paused:false,
		start:function(){
			if(this.paused)return;
			var t=this;
			if(t.timer==null){
				console.log('%s:live.start()',counter++);
				t.timer=setTimeout(function(){
					t.run();
				}, live_initial);
				monitor.update_status();
			}
		},
		stop:function(){
			console.log('%s:live.stop()',counter++);
			try{
				clearTimeout(this.timer);
			}finally{
				this.timer=null;
				monitor.update_status();
			}
		},
		pause:function(){
			console.log('%s:live.pause()',counter++);
			this.paused=true;
			this.stop();
			$('#Pause').text('Paused').animate({'width':70},200);
			try{clearTimeout(this.count_down_timer);}finally{}
			monitor.update_status();
		},
		resume:function(){
			console.log('%s:live.resume()',counter++);
			this.paused=false;
			this.start();
			var t=this;
			function cd(c){
				if(c<1){
					var $p=$('#Pause').text('Action');
					setTimeout(function(){
						$p.animate({'width':0},200,function(){$(this).hide();});
					},500)
					return;
				}else{
					$('#Pause').text(Math.round(c));
				}
				t.count_down_timer=setTimeout(function(){cd(c-1);},1000);
			};
			cd(Math.round(live_initial/1000));
			monitor.update_status();
		},
		run:function(){
			console.log('%s:live.run()', counter++);

			var t=this;
			t.timer=setTimeout(function(){
				t.run();
			}, live_interval);

			var i=monitor.get();
			// simple
			// $(i).hide().prependTo('#Timeline .tweets').slideDown();

			// 
			var $t=$(i).prependTo('#Timeline .tweets');
			var h=$t.height()+parseInt($t.css('padding-top'))+parseInt($t.css('padding-bottom'));
			$t.css({'margin-top':-h}).animate({'margin-top':0});//10*h

			monitor.update_status();
		}
	};

	var normal={
		start:function(){
			console.log('%s:normal.start()',counter++);
			if(monitor.size()>0){
				$('#Notifier').slideDown();
			}
			monitor.update_status();
		},
		stop:function(){
			console.log('%s:normal.stop()',counter++);
			$('#Notifier').hide();
			monitor.update_status();
		},
		pause:function(){monitor.update_status();},
		resume:function(){monitor.update_status();},
		run:function(){
			console.log('%s:normal.run()',counter++);
			$('#Notifier').hide();
			$('.separator').removeClass('separator');
			var ii=monitor.get_all().reverse();
			var $ii=$(ii);
			$ii.last().addClass('separator');
			$('#Timeline .tweets').prepend($ii);
			//$('#Timeline .tweets').prepend(ii.reverse());
			monitor.update_status();
		}
	};

	var mode=(getCookie('LM'))?live:normal;

	var producer={
		timer:null,
		start:function(){
			var t=this;
			if(t.timer==null){
				console.log('%s:producer.start()',counter++);
				t.timer=setTimeout(function(){
					t.run();
				}, interval);
			}
			monitor.update_status();
		},
		stop:function(){
			console.log('%s:producer.stop()',counter++);
			try{
				clearTimeout(this.timer);
			}finally{
				this.timer=null;
			}
			monitor.update_status();
		},
		run:function(){
			var t=this;
			t.timer = setTimeout(function(){
				if(!t.active){
					t.active=true;
					t.feed(function(){
						t.active=false;
						monitor.update_status();
						if(t.timer==null)return;//?
						t.run();
					});
				}
			},interval);
		},
		params:params,
		url:url,
		feed:function(callback){
			var t=this;
			$.ajax({
				'type':"GET",
				'url':t.url,
				'data':t.params,
				'dataType':'json',
				'success':function(d){
					if(d&&d.success){
						if(d.params)t.params=d.params;
						if(d.count>0){
							monitor.put($(d.tweets).filter(function(){return this.nodeType==1}).toArray().reverse());
							interval=(interval/decay)<min_interval?min_interval:(interval/decay);
						}else{
							interval=(interval*decay)>max_interval?max_interval:(interval*decay);
						}
						console.log('%s:producer.feed(), data.count=%s, interval=%s',counter++, d.count, interval);
					}
					callback(d);
				},
				'error':function(){
					callback();
				}
			});
		}
	};

	var monitor={
		capacity:1000,
		buffer:[],
		put:function(i){
			if($.isArray(i)){
				this.buffer.push.apply(this.buffer, i);
			}else{
				this.buffer.push(i);
			}
			console.log('%s:monitor.put(), length=%s',counter++,this.buffer.length);
			if(this.buffer.length>this.capacity){
				producer.stop();
			}
			if(this.buffer.length>0){
				mode.start();
			}
		},
		get:function(){
			var i=this.buffer.shift();
			console.log('%s:monitor.get(), length=%s',counter++,this.buffer.length);
			if(this.buffer.length<=this.capacity){
				producer.start();
			}
			if(this.buffer.length<=0){
				mode.stop();
			}
			return i;
		},
		get_all:function(){
			var i=this.buffer;
			this.buffer=[];
			console.log('%s:monitor.get_all(), length=%s',counter++,this.buffer.length);
			producer.start();
			mode.stop();
			return i;
		},
		size:function(){
			return this.buffer.length;
		},
		update_status:function(){
			var t=this;
			if(updateDate)updateDate();
			t.set_notifier_text();
			setTimeout(function(){t.set_title();}, 200);
		},
		set_notifier_text:function(){
			if(this.buffer.length>this.capacity){
				$('#Notifier').text(this.capacity+'+ new tweets.');
			}else if(this.buffer.length>1){
				$('#Notifier').text(this.buffer.length+' new tweets');
			}else if(this.buffer.length==1){
				$('#Notifier').text('1 new tweet.');
			}else{
				$('#Notifier').text('Look! A dragonfly. ');
			}
		},
		set_title:function(){
			if(mode.paused){
				document.title=otitle+' [Paused]';
				return;
			}
			if(this.buffer.length>this.capacity){
				document.title=otitle+' ('+this.capacity+'+)';
			}else if(this.buffer.length>0){
				document.title=otitle+' ('+this.buffer.length+')';
			}else{
				document.title=otitle;
			}
		}
	};

	var _={
		pause:function(){
			mode.pause();
		},
		resume:function(){
			mode.resume();
		},
		flush:function(){
			normal.run();
		},
		on:function(){
			mode=live;
			live.start();
			normal.stop();
			$('#Mode').text('Live Mode').addClass('live-mode');
			setCookie('LM','t',3600*24*30);
		},
		off:function(){
			mode=normal;
			normal.start();
			live.stop();
			$('#Mode').text('Live Mode').removeClass('live-mode');
			$('#Pause').animate({'width':0},200,function(){$(this).hide();});
			deleteCookie('LM');
		},
		start:function(){
			producer.start();
		}
	};

	$(function(){
		$('#Notifier').click(function(e){
			_.flush();
			e.preventDefault();
		});
		var paused=false;
		$(document).keydown(function(e){
			if(e.keyCode==27){//Esc
				if(paused){
					_.resume();
					paused=false;
				}else{
					_.pause();
					paused=true;
				}
			}
		});

		var hasFocus = true;
		var active_element;
		function setFocusEvents(){
			active_element = document.activeElement;
			if ($.browser.msie){
				$(document).bind('focusout',function(){onblur();});
				$(document).bind('focusin',function(){onfocus();});
			}else{
				$(window).bind('blur',function(){onblur();});
				$(window).bind('focus',function(){onfocus();});
			}
		}
		function onfocus()	{
			if(!hasFocus){
				_.resume();
			}
			hasFocus = true;
		}
		function onblur()	{
			if (active_element != document.activeElement) {
				active_element = document.activeElement;
				return;
			}
			if(hasFocus){
				_.pause();
			}
			hasFocus = false;
		}
		setFocusEvents();

		if(getCookie('LM')=='t'){
			$('#Mode').text('Live Mode').addClass('live-mode');
			$('#Mode').toggle(function(){_.off();},function(){_.on()});
		}else{
			$('#Mode').text('Live Mode').removeClass('live-mode');
			$('#Mode').toggle(function(){_.on();},function(){_.off()});
		}
	});

	return _;
}

//common actions
$(function(){
	$.ajaxSetup({
		'cache':false,
		'error':function(xhr,text){
			errorEndTip(text);
		},
		'timeout':10000
	});

	$('#Nav a, .screen_name a, .tweet-text a').live('click', function(e){
		var url=$(this).attr('href');
		var tar=$(this).attr('target');
		if(tar=='_blank'){
			return
		}else{
			startTinyTip('Loading...');
		}
		setTimeout(function(){
			window.location=url;
		},0);
		e.preventDefault();return false;
	});

	$(window).bind('scroll',function(){
		if($(window).scrollTop()>0){$('#ToTop,#LToTop').show();}
		else{$('#ToTop,#LToTop').hide();}

        if(!window.XMLHttpRequest){//ie6
			var st=$(document).scrollTop(),wh=$(window).height();
            $('#ToTop').css("top", st+wh-100-50);
            $('#LToTop').css("top", st+130);//TODO
        }
	});
	
	$('#ToTop,#LToTop').click(function(){
		var time=150;
		if($.browser.webkit){
			$("body").animate({scrollTop:0},time);
		}else{
			$("html").animate({scrollTop:0},time);
		}
	}).mouseover(function(){
		$(this).addClass('hover');
	}).mouseout(function(){
		$(this).removeClass('hover');
	});

});
