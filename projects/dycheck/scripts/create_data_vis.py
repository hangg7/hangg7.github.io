import argparse
import json
import os

import cv2
import imageio
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("dataset", type=str)
args = parser.parse_args()

if args.dataset == "dnerf":
    output_dir = "./assets/data_vis/dnerf/"
    root_dir = "/shared/hangg/datasets/dnerf/"
    seqs = os.listdir(root_dir)
    for seq in seqs:
        with open(
            os.path.join(root_dir, seq, "transforms_train.json"), "r"
        ) as fp:
            meta_data = json.load(fp)
        
        output_file = os.path.join(output_dir, seq, "train.mp4")
        print (output_file)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        writer = imageio.get_writer(output_file, fps=30)
        for fmeta in meta_data["frames"]:
            image_path = os.path.join(root_dir, seq, fmeta["file_path"] + ".png")
            image = imageio.imread(image_path)
            writer.append_data(image)
        writer.close()

elif args.dataset in ["nerfies", "hypernerf"]:
    output_dir = f"./assets/data_vis/{args.dataset}/"
    root_dir = f"./datasets/{args.dataset}"
    seqs = os.listdir(root_dir)
    for seq in seqs:
        print (seq)
        with open(
            os.path.join(root_dir, seq, "extra.json"), "r"
        ) as fp:
            meta_data = json.load(fp)
            fps = meta_data["fps"]

        with open(
            os.path.join(root_dir, seq, "dataset.json"), "r"
        ) as fp:
            meta_data = json.load(fp)
            train_ids = meta_data["train_ids"]
        output_file = os.path.join(output_dir, seq, "train.mp4")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        writer = imageio.get_writer(output_file, fps=fps)
        for train_id in train_ids:
            image_path = os.path.join(root_dir, seq, "rgb/4x", train_id + ".png")
            image = imageio.imread(image_path)
            writer.append_data(image)
        writer.close()

        with open(
            os.path.join(root_dir, seq, "dataset.json"), "r"
        ) as fp:
            meta_data = json.load(fp)
            ids = meta_data["ids"]
        for key in ["left", "right"]:
            output_file = os.path.join(output_dir, seq, f"{key}.mp4")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            writer = imageio.get_writer(output_file, fps=fps)
            for id in ids:
                if not (key in id):
                    continue
                image_path = os.path.join(root_dir, seq, "rgb/4x", id + ".png")
                image = imageio.imread(image_path)
                writer.append_data(image)
            writer.close()

        command = (
            'ffmpeg '
            '-y '
            f'-i {os.path.join(output_dir, seq, "left.mp4")} '
            f'-i {os.path.join(output_dir, seq, "right.mp4")} '
            f'-i {os.path.join(output_dir, seq, "train.mp4")} '
            '-filter_complex "[0]pad=iw+5:ih:color=white[0:v];[1]pad=iw+5:ih:color=white[1:v];[0:v][1:v][2:v]hstack=inputs=3[v]" -map "[v]" '
            f'{os.path.join(output_dir, seq, "all.mp4")}'
        )
        os.system(command)

elif args.dataset == "nsff":
    video_dir = "/home/ruilongli/data/NSFF/nvidia_data_full/"
    video_names = ["Balloon1-2", "Balloon2-2", "DynamicFace-2", "Jumping", "Playground", "Skating-2", "Truck-2", "Umbrella"]
    fps_list = [15, 30, 15, 30, 30, 30, 30, 15]
    cameras = ["cam%02d" % i for i in range(1, 12 + 1)]

    for video_name, fps in zip(video_names, fps_list):
        video_frames = sorted(
            os.listdir(os.path.join(video_dir, video_name, "dense", "mv_images"))
        )
        images_multiview = []
        for i, camera in enumerate(cameras):
            images = []
            for video_frame in video_frames:
                image_path = os.path.join(
                    video_dir, video_name, "dense", "mv_images", video_frame, "%s.jpg" % camera
                )
                image = imageio.imread(image_path)
                # image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
                images.append(image)
            images_multiview.append(images)
        images_multiview = np.array(images_multiview)

        frames = sorted(
            os.listdir(os.path.join(video_dir, video_name, "dense", "images"))
        )
        images_train = []
        for frame in frames:
            image_path = os.path.join(video_dir, video_name, "dense", "images", frame)
            image = imageio.imread(image_path)
            image = cv2.resize(image, (0, 0), fx=2, fy=2)
            images_train.append(image)
        images_train = np.stack(images_train)

        images_multiview[0][:, -10:] = 255
        images_multiview[2][:, -10:] = 255
        
        canvas = np.concatenate([
            np.concatenate([
                images_multiview[0],
                images_multiview[4],
            ], axis=-3),
            np.zeros((images_train.shape[0], images_train.shape[1], 10, 3), dtype=images_train.dtype) + 255,
            np.concatenate([
                images_multiview[2],
                images_multiview[6],
            ], axis=-3),
            np.zeros((images_train.shape[0], images_train.shape[1], 10, 3), dtype=images_train.dtype) + 255,
            images_train,
        ], axis=-2)

        output_file = os.path.join("assets/data_vis/nsff", video_name, "all.mp4")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        writer = imageio.get_writer(output_file, fps=fps)
        for img in canvas:
            img = cv2.resize(img, (0, 0), fx=0.3, fy=0.3)
            writer.append_data(img)
        writer.close()
