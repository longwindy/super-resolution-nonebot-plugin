from pathlib import Path
import sys

SAVE_DIR = Path("data/super_resolution/received_images")

MODEL = ['', 'realesrgan-x4plus', 'realesrgan-x4plus-anime', 'realesr-animevideov3']

BASE_DIR = Path(__file__).parent.resolve()

ROOT_DIR = Path(sys.modules['__main__'].__file__).parent.resolve()

INPUT_DIR = SAVE_DIR

OUTPUT_DIR = Path("data/super_resolution/processed_images")

MAX_SEND_IMAGE_SIZE = 20*1024*1024