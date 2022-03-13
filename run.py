import argparse
from poses_utils import show_poses, show_poses_from_npy, show_poses_from_npys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, help="工作方式")
    parser.add_argument('--scene', type=str, help='场景文件夹')
    parser.add_argument('--npy', type=str, help='npy文件')
    parser.add_argument('--npys', type=str, help='npy文件')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    if args.mode == "scene":
        show_poses(args.scene)
    elif args.mode == "npy":
        show_poses_from_npy(args.npy)
    elif args.mode == "npys":
        show_poses_from_npys(args.npys)
