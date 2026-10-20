import glob
from detector import detect

for path in glob.glob("images/*.jpg") + glob.glob("images/*.jpeg") + glob.glob("images/*.png"):
    print("\n=== Image:", path, "===")
    for d in detect(path):
        print(d)