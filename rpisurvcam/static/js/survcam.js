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

/* Updating stream status, events and sliders on page load and consistent polling: */
function updateStatus() {
    $.get( "/update-status",
           function(response) {
            refresh_stream_status(response.stream_status);
            $("#tiltSlider").slider('setValue',
                             parseInt(response.tilt_target));
            $("#panSlider").slider('setValue',
                             parseInt(response.pan_target));
            });
}

function updateStatusPolling() {
  updateStatus()
  setTimeout(updateStatusPolling, 4000);
}

/* On document load: */
$(document).ready(updateStatusPolling);

$('#tiltSlider').slider({
	formatter: function(value) {
		return value + '°';
	}
});

$('#panSlider').slider({
	formatter: function(value) {
		return value + '°';
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

// To keep the vertical slider height responsive
function fixTiltSliderHeight() {
    var h = $('#streamCol').height();
    if(h < 190) h = 190
    $('#tiltSliderCol').height(h)
}
$(window).resize(fixTiltSliderHeight);
$(window).load(fixTiltSliderHeight);

var stream_url = $(".stream-img").attr("src");

function refresh_stream_status(stream_alive) {
	if (stream_alive) {
    $("#stream-status").html("<strong>Status: </strong> Live").removeClass('list-group-item-danger').addClass('list-group-item-success');
    $(".stream-img").attr("src", stream_url);
	} else {
		$("#stream-status").html("<strong>Status: </strong> Down").removeClass('list-group-item-success').addClass('list-group-item-danger');
    $(".stream-img").attr("src", "static/img/stream_down.png");
	}
}


$(document).ready(function() {
  $("#tap-snapshot-alert").delay(300).addClass("in").delay(2500).fadeOut(1000);
});

$(".snapshot-btn").click(function() {
    $.ajax({
      type: 'GET',
      url: '/snapshot',
      success: function(response){
        document.location.href = '/snapshot'
      }
    });
});
