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
function refreshEvents(events_html) {
  $("#events-container").html(events_html);
}

var stream_url = $(".stream-img").attr("src");

function refreshStreamStatus(stream_status, stream_status_html) {
  $("#stream_status").html(stream_status_html);

  if (stream_status) {
    $(".stream-img").attr("src", stream_url);
  } else {
    $(".stream-img").attr("src", "static/img/stream_down.png");
  }
}

function updateStatus() {
    $.get( "/update-status",
           function(response) {
            refreshStreamStatus(response.stream_status,
                                response.stream_status_html);
            refreshEvents(response.events);
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

function showModal(modal_html) {
  $(".modal-body").html(modal_html);
  $("#modal").modal("show");
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
              $("#tiltSlider").slider('setValue', parseInt(response.target));
            })
        }
);

$('#panSlider').slider('on','slideStop',function() {
  $.post( "/move",
          { target: $('#panSlider').val(), axis: "pan" },
            function(response) {
              $("#panSlider").slider('setValue', parseInt(response.target));
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

$("#camera-on").click(function() {
  $.get("/camera-on");
  showModal(
      "<p>Camera turned on, please wait shortly for streaming to start.</p>");
});

$("#camera-off").click(function() {
  $.get("/camera-off");
  showModal(
      "<p>Camera turned off, streaming will now stop.</p>");
})
