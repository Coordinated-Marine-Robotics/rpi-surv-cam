function moveCamera(dir) {
	$.ajax({
		url:"move",
		data: { direction: dir }
	})
		.done(function(msg) {
			$("#last-action").text("Sent request to move camera to the " + dir + ".").show()
		});
}

$("#last-action").hide();

var interval;
$("#move_left").mousedown(function() {
	interval = setInterval(function() {moveCamera("left")}, 100);
});

$("#move_right").mousedown(function() {
        interval = setInterval(function() {moveCamera("right")}, 100);
});

$(document).mouseup(function() {
        clearInterval(interval);
});

