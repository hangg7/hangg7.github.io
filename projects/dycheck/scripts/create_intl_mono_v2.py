import glob
import os

import imageio
import numpy as np
from click import command
from PIL import Image, ImageDraw, ImageFont

# Teleportated Camera v.s. Monocular Camera
# fixed time move camera

jobs = [
    (
        "/shared/hangg/projects/dybench/work_dirs/hypernerf/vrig-peel-banana/ambient/mono/renders/video/val_common/",
        "/shared/hangg/projects/dybench/work_dirs/hypernerf/vrig-peel-banana/ambient/repro/renders/video/val_common/",
    ),
    (
        "/shared/hangg/projects/dybench/work_dirs/hypernerf/vrig-chicken/dense/mono/renders/video/val_common/",
        "/shared/hangg/projects/dybench/work_dirs/hypernerf/vrig-chicken/dense/repro/renders/video/val_common/",
    ),
    (
        "/shared/hangg/projects/dybench/work_dirs/hypernerf/vrig-3dprinter/tnerf/mono/renders/video/val_common/",
        "/shared/hangg/projects/dybench/work_dirs/hypernerf/vrig-3dprinter/tnerf/repro/renders/video/val_common/",
    ),
    (
        "/shared/hangg/projects/dybench/work_dirs/nerfies/broom/dense/mono/renders/video/val_common",
        "/shared/hangg/projects/dybench/work_dirs/nerfies/broom/dense/repro/renders/video/val_common",
    )
]

for path2, path1 in jobs:
    splits = path1.split("/")
    dataset = splits[6]
    seq = splits[7]
    model = {"tnerf": "tnerf", "dense": "nerfies", "ambient": "hypernerf"}[splits[8]]
    
    videos = []
    # video_path = sorted(glob.glob(os.path.join(path1, "*.mp4")))
    # videos.append(video_path[0])
    # video_path = sorted(glob.glob(os.path.join(path2, "*.mp4")))
    # videos.append(video_path[0])

    for path in [path1, path2]:
        video_path = sorted(glob.glob(os.path.join(path, "*.mp4")))[0]

        reader = imageio.get_reader(video_path)
        fps = reader.get_meta_data()['fps']

        images = []
        for i, im in enumerate(reader):
            fontpath = "./assets/unicode.timesu.ttf"     
            font = ImageFont.truetype(fontpath, 40)
            if path == path1:
                im[:40, :90] = 0
                img_pil = Image.fromarray(im)
                draw = ImageDraw.Draw(img_pil)
                draw.text((4, 4),  "Tele.", font=font, fill=(255, 255, 255))
                output_file = os.path.join("/tmp/", f"_dybench_intl.mp4")
            else:
                im[:40, :170] = 0
                img_pil = Image.fromarray(im)
                draw = ImageDraw.Draw(img_pil)
                draw.text((4, 4),  "Non-Tele.", font=font, fill=(255, 255, 255))
                output_file = os.path.join("/tmp/", f"_dybench_mono.mp4")
            img = np.array(img_pil)
            images.append(img)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        writer = imageio.get_writer(output_file, fps=fps)
        for image in images:
            writer.append_data(image)
        writer.close()
        videos.append(output_file)

    output_path = f'assets/intl_mono_v2/{dataset}/{seq}/{model}/'
    os.makedirs(output_path, exist_ok=True)
    command = (
        'ffmpeg -y '
        f'-i {videos[0]} '
        f'-i {videos[1]} '
        '-filter_complex "[0]pad=iw+5:color=white[left];[left][1]hstack=inputs=2" '
        f'{output_path}/video.mp4'
    )
    print (model, command)
    os.system(command)
