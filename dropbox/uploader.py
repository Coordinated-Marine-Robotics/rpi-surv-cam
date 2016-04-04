import os
import sys

CAPACITY_THRESH_MB = 10
MB_IN_BYTES = 1048576.0

dropbox_videos = "/videos"
dropbox_images = "/images"
dropbox_snapshots = "/snapshots"

def is_data_dir_full(motion_path):
	os.chdir(motion_path)
	curr_size = sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))
	curr_size_mb = curr_size / MB_IN_BYTES
	return (curr_size_mb > CAPACITY_THRESH_MB)

def upload_files(motion_path, dropbox_uploader_path):
	for motion_file in os.listdir(motion_path):
		file_to_upload = os.path.join(motion_path, motion_file)

		if not os.path.exists(file_to_upload):
		# While working the files were deleted -> we're done
			break

		cmd = dropbox_uploader_path + " upload " + file_to_upload + " "

		if file_to_upload.endswith(".jpg"):
			cmd += dropbox_snapshots if "snap" in motion_file else dropbox_images
		elif file_to_upload.endswith(".avi"):
			cmd += dropbox_videos
			
		os.system(cmd)
		os.system("rm " + file_to_upload)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Usage: python uploader.py <motion data dir> <dropbox_uploader script>."
		exit()

	if not os.path.isdir(sys.argv[1]):
		print "Missing or invalid Motion directory."
		exit()

	motion_path = sys.argv[1]
	dropbox_uploader_path = os.path.realpath(sys.argv[2])
	if not os.path.isfile(dropbox_uploader_path):
		print "Dropbox uploader script is missing at " + dropbox_uploader_path + "."
		exit()
	if is_data_dir_full(motion_path):
		print "Motion data directory is above capacity threshold - uploading to DropBox..."
		upload_files(motion_path, dropbox_uploader_path)
	else:
		print "Motion data directory is below capacity threshold - no need to upload to DropBox..."