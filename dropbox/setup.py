import os
import subprocess

# Remote directories' names
DROPBOX_VIDEOS = "/videos"
DROPBOX_IMAGES = "/images"

# Local settings path and names
SETTINGS_PATH = "/var/opt/platform_settings.py"
SETTING_NAME_VIDEOS = "DROPBOX_VIDEOS_URL"
SETTING_NAME_IMAGES = "DROPBOX_IMAGES_URL"

# Dropbox Uploader script path
dropbox_uploader = os.path.join(os.path.dirname(os.path.abspath(__file__)),'dropbox_uploader.sh')

# Makes a remote Dropbox directory, returns boolean indicating success.
def make_dropbox_dir(dropbox_uploader, path):
    print "Creating Dropbox directory: " + path
    proc = subprocess.Popen([dropbox_uploader, 'mkdir', path],
                            stdout=subprocess.PIPE)
    result = proc.stdout.read().split().pop()
    if result != 'DONE' and result != 'EXISTS':
        proc.kill()
        print " > An error occurred, aborting."
        return False
    else:
        print " > Created successfully."
        return True

# Shares a remote Dropbox directory, return the shared URL.
def share_dropbox_dir(dropbox_uploader, path):
    print "Getting shared URL for Dropbox directory: " + path
    proc = subprocess.Popen([dropbox_uploader, 'share', path],
                            stdout=subprocess.PIPE)
    # assuming output format:  > Share link: https://db.tt/a9xJoX9X
    shared_url = proc.stdout.read().split()[3]
    print " > Shared URL is: " + shared_url
    return shared_url

# Replace or add setting value to text representing the local settings file,
# and return the new settings text.
def set_setting_value(settings_text, setting_name, value):
    new_setting_text = "%s = '%s'" % (setting_name, value)
    setting_start = settings_text.find(setting_name)
    if setting_start == -1:
        # Setting doesn't exist, append it to end of settings
        return settings_text + "\n\n" + new_setting_text
    else:
        # Setting exists, update it's value
        setting_end = settings_text.find("\n", setting_start)
        return settings_text[:setting_start] + new_setting_text + settings_text[setting_end:]

###################### Script entry point ######################

# Create remote videos and images directories
if not (make_dropbox_dir(dropbox_uploader, DROPBOX_VIDEOS) and
        make_dropbox_dir(dropbox_uploader, DROPBOX_IMAGES)):
    # Quit if there was an issue while creating the directories
    exit()

# Share videos and images directories and get their URLs
videos_url = share_dropbox_dir(dropbox_uploader, DROPBOX_VIDEOS)
images_url = share_dropbox_dir(dropbox_uploader, DROPBOX_IMAGES)

# Write shared URLs to local settings file, to be used by web application
## Read current settings file contents
try:
    print "Reading settings file"
    current_settings_file = file(SETTINGS_PATH, 'r')
    current_settings = current_settings_file.read()
    current_settings_file.close()
    ## Update settings' values and write to the settings file
    print "Updating settings with Dropbox URLs"
    new_settings = set_setting_value(current_settings, SETTING_NAME_VIDEOS, videos_url)
    new_settings = set_setting_value(new_settings, SETTING_NAME_IMAGES, images_url)
    new_settings_file = file(SETTINGS_PATH,'w')
    new_settings_file.write(new_settings)
    new_settings_file.close()
    print " > Done"
except IOError as e:
    print " > An error occurred: " + str(e)
