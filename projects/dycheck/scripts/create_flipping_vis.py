import glob
import os

import cv2
import imageio
import numpy as np

from upload import path_parser, seqs


def create_mask(p1, p2, width, height):
    cx, cy = np.meshgrid(np.arange(width), np.arange(height))
    # y = ax + b
    x1, y1 = p1
    x2, y2 = p2
    a = (y2 - y1) / max(x2 - x1, 1e-10)
    b = y2 - a * x2
    mask = a * cx + b - cy < 0
    return mask


for dataset in ["nerfies", "hypernerf"]:
    for seq in seqs[dataset]:
        seq = "tmp"

        # full_path = path_parser(
        #     dataset=dataset, seq=seq, model="nerfies", variant="mono"
        # )
        full_path = "/shared/hangg/projects/dybench/work_dirs/hypernerf/vrig-peel-banana/ambient/mono/renders/video/val_common/"
        if full_path == "":
            continue
        video_path = sorted(glob.glob(os.path.join(full_path, "*.mp4")))[0]
        reader = imageio.get_reader(video_path)
        fps = reader.get_meta_data()['fps']
        images1 = np.stack([im for im in reader])
        nframes, height, width = images1.shape[:3]

        # full_path = path_parser(
        #     dataset=dataset, seq=seq, model="nerfies", variant="intl"
        # )
        full_path = "/shared/hangg/projects/dybench/work_dirs/hypernerf/vrig-peel-banana/ambient/repro/renders/video/val_common/"
        if full_path == "":
            continue
        video_path = sorted(glob.glob(os.path.join(full_path, "*.mp4")))[0]
        reader = imageio.get_reader(video_path)
        images2 = np.stack([im for im in reader])

        blends = []
        x_step = width / 20
        for i in range(0, 60):
            blends.append(images1[i])
        image1, image2 = images1[0], images2[0]
        for j in range(30):
            p1 = (0 + j * x_step, 0)
            p2 = (0 + j * x_step, height - 1)
            mask = create_mask(p1, p2, width, height).astype(image1.dtype)
            blend = image1 * (1 - mask[..., None]) + image2 * mask[..., None]
            cv2.line(blend, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (128, 128, 128), 1, lineType=cv2.LINE_AA) 
            blends.append(blend)
        for j in range(30):
            p1 = (width - j * x_step, 0)
            p2 = (width - j * x_step, height - 1)
            mask = create_mask(p1, p2, width, height).astype(image1.dtype)
            blend = image1 * (1 - mask[..., None]) + image2 * mask[..., None]
            cv2.line(blend, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (128, 128, 128), 1, lineType=cv2.LINE_AA) 
            blends.append(blend)
        for j in range(30):
            p1 = (0 + j * x_step, 0)
            p2 = (0 + j * x_step, height - 1)
            mask = create_mask(p1, p2, width, height).astype(image1.dtype)
            blend = image1 * (1 - mask[..., None]) + image2 * mask[..., None]
            cv2.line(blend, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (128, 128, 128), 1, lineType=cv2.LINE_AA) 
            blends.append(blend)
        for i in range(60):
            blends.append(images2[i])
        for j in range(30):
            p1 = (width - j * x_step, 0)
            p2 = (width - j * x_step, height - 1)
            mask = create_mask(p1, p2, width, height).astype(image1.dtype)
            blend = image1 * (1 - mask[..., None]) + image2 * mask[..., None]
            cv2.line(blend, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (128, 128, 128), 1, lineType=cv2.LINE_AA) 
            blends.append(blend)
        for j in range(30):
            p1 = (0 + j * x_step, 0)
            p2 = (0 + j * x_step, height - 1)
            mask = create_mask(p1, p2, width, height).astype(image1.dtype)
            blend = image1 * (1 - mask[..., None]) + image2 * mask[..., None]
            cv2.line(blend, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (128, 128, 128), 1, lineType=cv2.LINE_AA) 
            blends.append(blend)
        for j in range(30):
            p1 = (width - j * x_step, 0)
            p2 = (width - j * x_step, height - 1)
            mask = create_mask(p1, p2, width, height).astype(image1.dtype)
            blend = image1 * (1 - mask[..., None]) + image2 * mask[..., None]
            cv2.line(blend, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (128, 128, 128), 1, lineType=cv2.LINE_AA) 
            blends.append(blend)

        output_file = f"assets/flipping/{dataset}/{seq}.mp4"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        writer = imageio.get_writer(output_file, fps=fps)
        for blend in blends:
            writer.append_data(blend)
        writer.close()

        exit()
