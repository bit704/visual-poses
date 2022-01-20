import argparse
from poses_utils import show_poses


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', type=str, help='场景文件夹')
    return parser.parse_args()


if __name__ == '__main__':
    show_poses(get_args().scene)
