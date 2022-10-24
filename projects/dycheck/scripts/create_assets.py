import glob
import os

import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from upload import datasets, models, path_parser, seqs

# Teleportated Camera v.s. Monocular Camera
# fixed time move camera
for dataset in ["nerfies", "hypernerf"]:
    for seq in seqs[dataset]:
        for model in models:
            videos = []
            for variant in ["intl", "mono"]:
                full_path = path_parser(dataset, seq, model, variant)
                if full_path == "":
                    continue
                video_path = sorted(glob.glob(os.path.join(full_path, "*.mp4")))[1]
                # videos.append(video_path)

                reader = imageio.get_reader(video_path)
                fps = reader.get_meta_data()['fps']

                images = []
                for i, im in enumerate(reader):
                    fontpath = "./assets/unicode.timesu.ttf"     
                    font = ImageFont.truetype(fontpath, 40)
                    if variant == "intl":
                        im[:40, :90] = 0
                        img_pil = Image.fromarray(im)
                        draw = ImageDraw.Draw(img_pil)
                        draw.text((4, 4),  "Tele.", font=font, fill=(255, 255, 255))
                    else:
                        im[:40, :170] = 0
                        img_pil = Image.fromarray(im)
                        draw = ImageDraw.Draw(img_pil)
                        draw.text((4, 4),  "Non-Tele.", font=font, fill=(255, 255, 255))
                    img = np.array(img_pil)
                    images.append(img)

                output_file = os.path.join("/tmp/", f"_dybench_{variant}.mp4")
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                writer = imageio.get_writer(output_file, fps=fps)
                for image in images:
                    writer.append_data(image)
                writer.close()
                videos.append(output_file)
                        
            output_path = f'assets/intl_mono/{dataset}/{seq}/{model}/'
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

# # benchmarking
# for dataset in datasets:
#     for seq in seqs[dataset]:
#         videos = []
#         for model in models:
#             if dataset == "iphone":
#                 variant = "mono" if model == "nsff" else "bkgd_depth_dist"
#             else:
#                 variant = "mono"
#             full_path = path_parser(dataset, seq, model, variant)
#             if full_path == "":
#                 continue
#             video_path = sorted(glob.glob(os.path.join(full_path, "*.mp4")))[0]
#             videos.append(video_path)
#         if len(videos) < 4:
#             continue
#         output_path = f'assets/benchmarking/{dataset}/{seq}/'
#         os.makedirs(output_path, exist_ok=True)
#         command = (
#             'ffmpeg '
#             '-y '
#             f'-i {videos[0]} '
#             f'-i {videos[1]} '
#             f'-i {videos[2]} '
#             f'-i {videos[3]} '
#             '-filter_complex "[0]pad=iw+5:ih:color=white[0:v];[1]pad=iw+5:ih:color=white[1:v];[2]pad=iw+5:ih:color=white[2:v];[0:v][1:v][2:v][3:v]hstack=inputs=4[v]" -map "[v]" '
#             f'{output_path}/video.mp4'
#         )
#         print (model, command)
#         os.system(command)


# # pro tips
# dataset = "iphone"
# model = "nerfies"
# for seq in seqs[dataset]:
#     videos = []
#     for variant in ["mono", "bkgd", "bkgd_depth", "bkgd_depth_dist"]:
#         full_path = path_parser(dataset, seq, model, variant)
#         if full_path == "":
#             continue
#         video_path = sorted(glob.glob(os.path.join(full_path, "*.mp4")))[0]
#         videos.append(video_path)
#     if len(videos) < 4:
#         continue
#     output_path = f'assets/pro_tips/{dataset}/{seq}/'
#     os.makedirs(output_path, exist_ok=True)
#     command = (
#         'ffmpeg '
#         '-y '
#         f'-i {videos[0]} '
#         f'-i {videos[1]} '
#         f'-i {videos[2]} '
#         f'-i {videos[3]} '
#         '-filter_complex "[0]pad=iw+5:ih:color=white[0:v];[1]pad=iw+5:ih:color=white[1:v];[2]pad=iw+5:ih:color=white[2:v];[0:v][1:v][2:v][3:v]hstack=inputs=4[v]" -map "[v]" '
#         f'{output_path}/video.mp4'
#     )
#     print (model, command)
#     os.system(command)
