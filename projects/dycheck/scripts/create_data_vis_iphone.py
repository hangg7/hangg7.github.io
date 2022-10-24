import multiprocessing
import os
import sys

import cv2
import imageio
import numpy as np
from dybench.datasets import Record3DProcessor
from PIL import Image, ImageDraw, ImageFont

EXPERIMENTS = [
    ("iphone2/apple", "/home/hangg/datasets/iphone/record3d"),
    ("iphone2/block", "/shared/hangg/datasets/iphone/record3d"),
    ("iphone2/paper-windmill", "/home/hangg/datasets/iphone/record3d"),
    ("iphone2/space-out", "/home/hangg/datasets/iphone/record3d"),
    ("iphone2/spin", "/home/hangg/datasets/iphone/record3d"),
    ("iphone2/teddy", "/shared/hangg/datasets/iphone/record3d"),
    ("iphone2/wheel", "/home/hangg/datasets/iphone/record3d"),
]

output_dir = "assets/data_vis_iphone/"
def process(job):
    EXPERIMENT, DATA_DIR = job
    DATASET, SEQUENCE = EXPERIMENT.split("/")

    processor = Record3DProcessor(SEQUENCE, [""], data_root=DATA_DIR)
    processor._process_train_points()
    processor._process_train_cameras()
    processor._process_train_rgbas_depths()
    processor._process_val_rgbas()

    train_imgs = processor.train_rgbas[..., :3]
    val_imgs = [v[..., :3] for v in processor.val_rgbas]
    val_bad_frames = processor.val_bad_frames

    reader = imageio.get_reader(f"./datasets/{EXPERIMENT}/visual/train.mp4")
    fps = reader.get_meta_data()['fps']
    images = np.stack([im for im in reader])
    width = images.shape[2] // 4

    for i, (v, vi) in enumerate(zip(val_imgs, val_bad_frames)):
        v = v.copy()
        if len(vi) > 0:
            v[vi] = cv2.addWeighted(v[vi], 0.5, 0, 0.5, 0)
            for j in vi:
                fontpath = "./assets/unicode.timesu.ttf"     
                font = ImageFont.truetype(fontpath, 80)
                v[j][:80, :330] = 0
                img_pil = Image.fromarray(v[j])
                draw = ImageDraw.Draw(img_pil)
                draw.text((10, 10),  "Excluded", font=font, fill=(255, 255, 255))
                img = np.array(img_pil)
                v[j] = img

        output_file = os.path.join(output_dir, SEQUENCE, f"val_{i}.mp4")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        writer = imageio.get_writer(output_file, fps=fps)
        for image in v:
            writer.append_data(image)
        writer.close()

    output_file = os.path.join(output_dir, SEQUENCE, "train.mp4")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    writer = imageio.get_writer(output_file, fps=fps)
    for image in train_imgs:
        writer.append_data(image)
    writer.close()

    output_file = os.path.join(output_dir, SEQUENCE, "depth.mp4")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    writer = imageio.get_writer(output_file, fps=fps)
    for image in images[:, :, width * 1: width * 2]:
        writer.append_data(image)
    writer.close()

    output_file = os.path.join(output_dir, SEQUENCE, "mask.mp4")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    writer = imageio.get_writer(output_file, fps=fps)
    for image in images[:, :, width * 2: width * 3]:
        writer.append_data(image)
    writer.close()

    command = (
        'ffmpeg '
        '-y '
        f'-i {os.path.join(output_dir, SEQUENCE, "depth.mp4")} '
        f'-i {os.path.join(output_dir, SEQUENCE, "mask.mp4")} '
        '-filter_complex "[0]crop=in_w:in_h-10[0:v];[0:v]pad=iw:ih+10:color=white[0:vv];[0:vv][1]vstack=inputs=2[vv];[vv]scale=w=iw/2:h=ih/2[v]" -map "[v]" '
        f'{os.path.join("/tmp/", f"_iphone_{SEQUENCE}.mp4")}'
    )
    os.system(command)
    if len(val_imgs) == 2:
        command = (
            'ffmpeg '
            '-y '
            f'-i {os.path.join(output_dir, SEQUENCE, f"val_0.mp4")} '
            f'-i {os.path.join(output_dir, SEQUENCE, f"val_1.mp4")} '
            f'-i {os.path.join(output_dir, SEQUENCE, f"train.mp4")} '
            f'-i {os.path.join("/tmp/", f"_iphone_{SEQUENCE}.mp4")} '
            '-filter_complex "[0]pad=iw+10:ih:color=white[0:v];[1]pad=iw+10:ih:color=white[1:v];[2]pad=iw+10:ih:color=white[2:v];[0:v][1:v][2:v][3]hstack=inputs=4[vv];[vv]scale=w=iw/3:h=ih/3[v]" -map "[v]" '
            f'{os.path.join(output_dir, SEQUENCE, f"all.mp4")}'
        )
        os.system(command)
    else:
        command = (
            'ffmpeg '
            '-y '
            f'-i {os.path.join(output_dir, SEQUENCE, f"val_0.mp4")} '
            f'-i {os.path.join(output_dir, SEQUENCE, f"train.mp4")} '
            f'-i {os.path.join("/tmp/", f"_iphone_{SEQUENCE}.mp4")} '
            '-filter_complex "[0]pad=iw+10:ih:color=white[0:v];[1]pad=iw+10:ih:color=white[1:v];[0:v][1:v][2]hstack=inputs=3[vv];[vv]scale=w=iw/3:h=ih/3[v]" -map "[v]" '
            f'{os.path.join(output_dir, SEQUENCE, f"all.mp4")}'
        )
        os.system(command)


if __name__ == "__main__":
    jobs = EXPERIMENTS
    pool = multiprocessing.Pool(processes=12)
    for i, _ in enumerate(pool.imap_unordered(process, jobs)):
        pass
    sys.stderr.write("\ndone.\n")
