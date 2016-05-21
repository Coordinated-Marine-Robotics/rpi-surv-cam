# RabbitMQueue name for commands sent from web app to servos
SERVO_CMD_QUEUE = 'servo_cmd'

# Motion software TCP stream port
# Should be the same as in /etc/motion/motion.conf under stream_port
MOTION_STREAM_PORT = 8081

# Motion software HTTP control port
# Should be the same as in /etc/motion/motion.conf under webcontrol_port
MOTION_CONTROL_PORT = 8082

# Motion software target directory for snapshots and motion videos
# Should be the same as in /etc/motion/motion.conf under target_dir
MOTION_TARGET_DIR = '/home/pi/motion_data'

# Motion software binary path
MOTION_BIN_PATH = '/usr/bin/motion'

# UV4L server port for web control interface - chosen when running uv4l
UV4L_SERVER_PORT = 9090

# Shared URL for Dropbox videos directory
DROPBOX_VIDEOS_URL = ''

# Shared URL for Dropbox images directory
DROPBOX_IMAGES_URL = ''
