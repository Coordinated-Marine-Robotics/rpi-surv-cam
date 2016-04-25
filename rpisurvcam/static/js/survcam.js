/* CSRF Protection Code: */

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/* End of CSRF Protection Code */

/* Updating sliders on page loading and consistent polling: */
function updateSliders() {
    $.get( "/update-target",
           function(response) {
            $("#tiltSlider").slider('setValue',
                             parseInt(response.tilt_target));
            $("#panSlider").slider('setValue',
                             parseInt(response.pan_target));
            });
}

function updateSlidersPolling() {
  updateSliders()
  setTimeout(updateSlidersPolling, 4000);
}

/* On document load: */
$(document).ready(updateSlidersPolling);

$('#tiltSlider').slider({
	formatter: function(value) {
		return 'Current value: ' + value;
	}
});

$('#panSlider').slider({
	formatter: function(value) {
		return 'Current value: ' + value;
	}
});

$('#tiltSlider').slider('on','slideStop',function() {
                $.post( "/move",
                        { target: $('#tiltSlider').val(), axis: "tilt" },
                        function(response) {
                            $("#tiltSlider").slider('setValue',
                                             parseInt(response.target));
                        })
         }
);

$('#panSlider').slider('on','slideStop',function() {
                $.post( "/move",
                        { target: $('#panSlider').val(), axis: "pan" },
                        function(response) {
                            $("#panSlider").slider('setValue',
                                             parseInt(response.target));
                        })
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

