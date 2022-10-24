import glob
import multiprocessing
import os
import sys

import tqdm

datasets = ["nerfies", "hypernerf", "iphone"]
seqs = {dataset: os.listdir(os.path.join("work_dirs", dataset)) for dataset in datasets}
models = ["tnerf", "nerfies", "hypernerf", "nsff"]
variants = ["intl", "mono", "bkgd", "bkgd_depth", "bkgd_depth_dist"]


def path_parser(dataset, seq, model, variant):
    # non-valid combinations
    if model == "nsff" and variant in ["bkgd", "bkgd_depth", "bkgd_depth_dist"]:
        return ""
    if dataset == "iphone" and variant == "intl":
        return ""
    if dataset in ["nerfies", "hypernerf"] and variant in ["bkgd", "bkgd_depth", "bkgd_depth_dist"]:
        return ""
    
    # process nsff seperately
    if model == "nsff":
        dataset_path = {
            "nerfies": "nerfies.31b562f", "iphone": "iphone2.31b562f", "hypernerf": "hypernerf.31b562f"
        }[dataset]
        dataset_path = os.path.join("/home/hangg/projects/nsff_pl/results/", dataset_path)
        seq_path = seq if dataset == "iphone" else f"{seq}_{variant}"
        model_path = ""
        if dataset == "iphone":
            variant_path = f"video/train"
        else:
            variant_path = f"video/train_{variant}"
        video_path = ""
    
    else:
        dataset_path = {"nerfies": "nerfies", "iphone": "iphone2", "hypernerf": "hypernerf"}[dataset]
        if dataset == "iphone" and variant == "mono":
            dataset_path = "iphone"
        dataset_path = os.path.join("/home/hangg/projects/dybench/work_dirs/", dataset_path)
        seq_path = seq
        model_path = {"tnerf": "tnerf", "nerfies": "dense", "hypernerf": "ambient"}[model]
        if dataset == "iphone":
            variant_path = {
                "mono": "base", "bkgd": "base", "bkgd_depth": "depth", "bkgd_depth_dist": "depth_dist"
            }[variant]
            video_path = f"renders/video/train"
        else:
            variant_path = {"mono": "mono_undistort", "intl": "repro"}[variant]
            video_path = f"renders/video/train_{variant}"

    full_path = os.path.join(
        dataset_path, seq_path, model_path, variant_path, video_path
    )
    files = glob.glob(os.path.join(full_path, "*.mp4"))

    if len(files) == 0:
        # Missing files:
        # iphone spin tnerf mono /home/hangg/projects/dybench/work_dirs/iphone/spin/tnerf/base/renders/video/train 0
        # iphone spin nerfies mono /home/hangg/projects/dybench/work_dirs/iphone/spin/dense/base/renders/video/train 0
        # iphone spin hypernerf mono /home/hangg/projects/dybench/work_dirs/iphone/spin/ambient/base/renders/video/train 0
        # iphone creeper tnerf mono /home/hangg/projects/dybench/work_dirs/iphone/creeper/tnerf/base/renders/video/train 0
        # iphone creeper nerfies mono /home/hangg/projects/dybench/work_dirs/iphone/creeper/dense/base/renders/video/train 0
        # iphone creeper hypernerf mono /home/hangg/projects/dybench/work_dirs/iphone/creeper/ambient/base/renders/video/train 0
        print (dataset, seq, model, variant, full_path, len(files))
        return ""
    else:
        return full_path


def upload_func(job, only_mkdir=False):
    dataset, seq, model, variant = job
    full_path = path_parser(dataset, seq, model, variant)
    if not os.path.exists(full_path):
        return
    dst_path = os.path.join(
        "remote_ucb:dybench_release/results/", dataset, seq, model, variant
    )
    if only_mkdir:
        command = f"rclone mkdir {dst_path}"
        os.system(command)
    else:
        print (dataset, seq, model, variant)
        command = f"rclone copy {full_path} {dst_path}"
        os.system(command)


if __name__ == "__main__":
    jobs = []
    for dataset in datasets:
        for seq in seqs[dataset]:
            for model in models:
                for variant in variants:
                    jobs.append((dataset, seq, model, variant))
    
    for job in tqdm.tqdm(jobs):
        upload_func(job, only_mkdir=False)

    # pool = multiprocessing.Pool(processes=12)
    # for i, _ in enumerate(pool.imap_unordered(upload_func, jobs)):
    #     pass
    # sys.stderr.write("\ndone.\n")
