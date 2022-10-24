import multiprocessing
import os
import sys

import imageio
import numpy as np

output_dir = "assets/data_vis_iphone/"
root_dir = "./datasets/iphone2/"
seqs = os.listdir(root_dir)

def process(seq):
    if os.path.exists(
        os.path.join(root_dir, seq, "visual", "val.mp4")
    ):
        return
    reader = imageio.get_reader(f"./{root_dir}/{seq}/visual/train.mp4")
    fps = reader.get_meta_data()['fps']
    images = np.stack([im for im in reader])
    width = images.shape[2] // 4

    output_file = os.path.join(output_dir, seq, "train.mp4")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    writer = imageio.get_writer(output_file, fps=fps)
    for image in images[:, :, width * 0: width * 1]:
        writer.append_data(image)
    writer.close()
    
    output_file = os.path.join(output_dir, seq, "depth.mp4")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    writer = imageio.get_writer(output_file, fps=fps)
    for image in images[:, :, width * 1: width * 2]:
        writer.append_data(image)
    writer.close()

    output_file = os.path.join(output_dir, seq, "mask.mp4")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    writer = imageio.get_writer(output_file, fps=fps)
    for image in images[:, :, width * 2: width * 3]:
        writer.append_data(image)
    writer.close()

    command = (
        'ffmpeg '
        '-y '
        f'-i {os.path.join(output_dir, seq, f"train.mp4")} '
        f'-i {os.path.join(output_dir, seq, f"depth.mp4")} '
        f'-i {os.path.join(output_dir, seq, f"mask.mp4")} '
        '-filter_complex "[0]pad=iw+10:ih:color=white[0:v];[1]pad=iw+10:ih:color=white[1:v];[0:v][1:v][2]hstack=inputs=3[vv];[vv]scale=w=iw/3:h=ih/3[v]" -map "[v]" '
        f'{os.path.join(output_dir, seq, f"all.mp4")}'
    )
    os.system(command)


if __name__ == "__main__":
    jobs = seqs
    pool = multiprocessing.Pool(processes=14)
    for i, _ in enumerate(pool.imap_unordered(process, jobs)):
        pass
    sys.stderr.write("\ndone.\n")
