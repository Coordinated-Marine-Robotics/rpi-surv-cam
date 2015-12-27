sudo pkill uv4l
sudo uv4l -nopreview --auto-video_nr --driver raspicam --encoding mjpeg --width 1024 --height 768 --framerate 30 --server-option '--port=9090' --server-option '--max-queued-connections=30' --server-option '--max-streams=25' --server-option '--max-threads=29'
