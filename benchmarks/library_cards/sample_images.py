#create random sample of 1000 images from 1-680671, put into /images folder
#images are on remote UB machine
#images are organized in sub-folders with 8 digits with 200 images each, ie the first 200 are in folder 00000000, the next in folder 00000200 
import random
import math
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

N = 1000
ssh_address = os.getenv("SSH_ADDRESS")
print(ssh_address)
remote_basepath = (os.getenv("REMOTE_BASEPATH"))
print(remote_basepath)
sample = random.sample(range(0, 680671), N)
os.system(f"wsl ssh-copy-id {ssh_address}")
for n in sample:
    subdir = int(math.floor(n / 200.0)) * 200
    remote_path = remote_basepath +  "/" + str(subdir).zfill(8) + "/" + str(n).zfill(8) + ".png"
    print(remote_path)
    os.system(f"wsl rsync -av --no-R {ssh_address}:{remote_path} ./images/{str(n).zfill(8)}.png")