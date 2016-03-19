$('#ex1').slider({
	formatter: function(value) {
		return 'Current value: ' + value;
	}
});

$('#ex2').slider({
	formatter: function(value) {
		return 'Current value: ' + value;
	}
});

$('#ex1').slider('on','slideStop',function() {
                $.ajax( {
                        url:"move",
                        data: {target: $('#ex1').val(), axis: "tilt"}
                } )
         }
);

$('#ex2').slider('on','slideStop',function() {
                $.ajax( {
                        url:"move",
                        data: {target: $('#ex2').val(), axis: "pan"}
                } )
         }
);

var $image = $("#stream-img");

$image.error(function() {
$("#stream-status").html("<strong>Status: </strong> Down").removeClass('list-group-item-success').addClass('list-group-item-danger');
});

/*
$.ajaxSetup({
    timeout: 500 //Time in milliseconds
});
*/

function refresh_stream () {
	var $downloadingImage = $("<img>");
	$downloadingImage.load(/* $image.attr("src"),*/
		function(response, lstatus, xhr) {
       		 	if (lstatus == "error") {
				$("#stream-status").html("<strong>Status: </strong> Down").removeClass('list-group-item-success').addClass('list-group-item-danger');
			} else {
				$("#stream-status").html("<strong>Status: </strong> Live").removeClass('list-group-item-danger').addClass('list-group-item-success');
  				$image.attr("src", $(this).attr("src"));
			}
		}
	);
	$downloadingImage.attr("src", $image.attr("src"));
}

refresh_stream();
setInterval(refresh_stream ,2000);

