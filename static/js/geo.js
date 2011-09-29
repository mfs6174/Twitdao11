$(function(){
	var count=0;
	var max_count=5;
	function success(pos){
		$('#TweetForm form')
		.append('<input type="hidden" name="lat" value="'+pos.coords.latitude+'" />')
		.append('<input type="hidden" name="long" value="'+pos.coords.longitude+'" />');
	}
	function error(e){
		switch(e.code){
			case e.PERMISSION_DENIED:
				break;
			case e.POSITION_UNAVAILABLE:
				break;
			case e.TIMEOUT:
				if(count++ < max_count){
					navigator.geolocation.getCurrentPosition(success, error);
				}
				break;
		}
	}
	if(navigator.geolocation){
		navigator.geolocation.getCurrentPosition(success, error);
	}
});