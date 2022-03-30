import argparse
from poses_utils import show_poses, show_poses_from_npy, show_poses_from_npys, show_poses_from_json, generate_newposes_from_json


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, help="工作方式")
    parser.add_argument('--scene', type=str, help='场景文件夹')
    parser.add_argument('--npy', type=str, help='npy文件')
    parser.add_argument('--npys', type=str, help='npy文件')
    parser.add_argument('--json', type=str, help='json文件')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    # 从一个照片文件夹里生成并绘制相机参数
    if args.mode == "scene":
        show_poses(args.scene)
    # 从一个npy文件里绘制相机参数（来自nerf-dev里load_llff.py里load_llff_data函数加载处理后的poses）
    elif args.mode == "npy":
        show_poses_from_npy(args.npy)
    # 从一组npy文件里绘制相机参数
    elif args.mode == "npys":
        show_poses_from_npys(args.npys)
    # 从一个json文件里绘制相机参数（来自instant-ngp的real nerf的输入数据集的json）
    elif args.mode == "json":
        show_poses_from_json(args.json)
    # 生成新的相机参数用于绘制图片
    elif args.mode == "generate_poses":
        generate_newposes_from_json(args.json)
