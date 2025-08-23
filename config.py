from pathlib import Path
import sys

# Relative path of the ROOT_DIR (bot.py)
SAVE_DIR = Path("data/super_resolution/received_images")

MODEL = ['', 'realesrgan-x4plus', 'realesrgan-x4plus-anime', 'realesr-animevideov3']

UNIVERSAL_INFO_HEADER = "[Super-resulution][INFO]"

# Absolute path of this config.py file
BASE_DIR = Path(__file__).parent.resolve()

# Absolute path of the main function (in bot.py)
ROOT_DIR = Path(sys.modules['__main__'].__file__).parent.resolve()

INPUT_DIR = SAVE_DIR

# Relative path of the ROOT_DIR (bot.py)
OUTPUT_DIR = Path("data/super_resolution/processed_images")

# Maximum send size (in bytes). The image will be sent by file if the file size is greater than this
# # Default: 20*1024*1024 (20MB)
MAX_SEND_IMAGE_SIZE = 20*1024*1024

# Maximum save size (in bytes) in received image folder
# Default: 512*1024*1024 (512MB)
MAX_RECEIVED_FOLDER_SIZE = 512*1024*1024

# Maximum save size (in bytes) in processed image folder
# Default: 1024*1024*1024 (1024MB)
MAX_PROCESSED_FOLDER_SIZE = 1024*1024*1024

# User will be warned if the image size greater than WARNING_SIZE
# Default: 2*1024*1024 (2MB)
WARNING_SIZE = 2*1024*1024

# Execution will be rejected if the image size greater than MAX_SIZE
# Default: 5*1024*1024 (5MB)
MAX_SIZE = 5*1024*1024

SUFFIX = ['', '.jpg', '.png']