import matplotlib.pyplot as plt
from colmap_utils import *
from scipy.spatial.transform import Rotation as R


def show_poses(scene_dir):
    # 生成相机参数
    generate_poses(scene_dir)
    # 读取相机参数
    poses = read_poses(scene_dir)
    # 绘制世界坐标系中的相机坐标系
    plot_poses(poses)


def generate_poses(scene_dir):
    print("场景文件夹", scene_dir)
    files_needed = ['{}.bin'.format(f) for f in ['cameras', 'images', 'points3D']]
    if os.path.exists(os.path.join(scene_dir, 'sparse/0')):
        files_had = os.listdir(os.path.join(scene_dir, 'sparse/0'))
    else:
        files_had = []
    if not all([f in files_had for f in files_needed]):
        print('运行COLMAP')
        # 运行colmap, 生成相机参数
        run_colmap(scene_dir)
    else:
        print('已有相机参数，无需运行COLMAP')


def read_poses(scene_dir):
    # 求得相机内参数
    camerasfile = os.path.join(scene_dir, 'sparse/0/cameras.bin')
    camdata = read_cameras_binary(camerasfile)
    cam = camdata[list(camdata.keys())[0]]
    h, w, f = cam.height, cam.width, cam.params[0]
    print('高', h, '宽', w, '焦距', f, '（单位:像素）')

    # 求得相机外参数
    imagesfile = os.path.join(scene_dir, 'sparse/0/images.bin')
    imdata = read_images_binary(imagesfile)
    # 场景中所有照片
    images_name = os.listdir(os.path.join(scene_dir, 'images'))
    imnum = len(images_name)  # 场景照片数量
    if imnum != len(imdata):
        print('未能生成所有照片的相机参数')
        # 识别的所有照片
        recog_images_name = []
        for i in range(1, len(imdata) + 1):
            recog_images_name.append(imdata[i].name)
        not_recog_images_name = [name for name in images_name if name not in recog_images_name]
        print('未识别的照片', not_recog_images_name)
        return
    else:
        print('成功生成全部{}张照片的相机外参数'.format(imnum))
    poses = []
    for _, image in imdata.items():
        # 取出相机外参数的四元数和位移向量
        poses.append((image.qvec, image.tvec))
    return poses


def plot_poses(poses):
    # 根据四元数求得旋转矩阵。旋转矩阵每一个列向量都是单位向量，且两两正交。
    # m = qvec2rotmat(poses[0][0])
    # print(np.linalg.norm(m[:, 0]))
    # print(np.inner(m[:, 0], m[:, 1]))

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    tvecs = []
    for pose in poses:
        # 四元数
        qvec = pose[0]
        # 位移向量
        tvec = pose[1]
        # 四元数 -> 旋转矩阵
        rotmat = qvec2rotmat(qvec)
        tvec = tvec.reshape([3, 1])
        bottom = np.array([0, 0, 0, 1.]).reshape([1, 4])
        # 拼接得到4*4相机矩阵w2c
        m = np.concatenate([np.concatenate([rotmat, tvec], 1), bottom], 0)
        # 矩阵求逆得到c2w
        m = np.linalg.inv(m)
        # 求得新的旋转矩阵和位移向量
        rotmat = m[0:3, 0:3]
        tvec = m[0:3, 3].reshape([3])

        x = np.matmul(rotmat, np.array([1, 0, 0]))
        y = np.matmul(rotmat, np.array([0, 1, 0]))
        z = np.matmul(rotmat, np.array([0, 0, 1]))
        for p, color in ((x, 'red'), (y, 'blue'), (z, 'green')):
            # 只画z轴
            if color != 'green':
                continue
            # 向量起点、向量方向（以原点为起点时向量的终点）、箭头长度比例、箭身长度比例、颜色
            ax.quiver(tvec[0], tvec[1], tvec[2],
                      p[0], p[1], p[2],
                      arrow_length_ratio=0.2,
                      length=2 if color == 'green' else 0.2,  # z轴画的长一些
                      color=color)
        tvecs.append(tvec)
    # 连线，绘制相机运动轨迹
    # for i in range(len(tvecs) - 1):
    #     ax.plot([tvecs[i][0], tvecs[i + 1][0]],
    #             [tvecs[i][1], tvecs[i + 1][1]],
    #             [tvecs[i][2], tvecs[i + 1][2]],
    #             color='black')

    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_zlim(0, 5)
    plt.show()


def plot_poses_NeRF(poses, z_color, ax):
    # 绘制NeRF里的poses
    # z_color，绘制相机坐标系里z轴的颜色
    tvecs = []
    for i in range(0, poses.shape[0]):
        bottom = np.array([0, 0, 0, 1.]).reshape([1, 4])
        pose = poses[i][..., :4]
        # 拼接得到4*4相机矩阵c2w
        m = np.concatenate([pose, bottom], 0)
        # 求得旋转矩阵和位移向量
        rotmat = m[0:3, 0:3]
        # 不修改符号的话，箭头朝向会出现错误
        rotmat[..., 1] = -rotmat[..., 1]
        rotmat[..., 2] = -rotmat[..., 2]
        tvec = m[0:3, 3].reshape([3])

        x = np.matmul(rotmat, np.array([1, 0, 0]))
        y = np.matmul(rotmat, np.array([0, 1, 0]))
        z = np.matmul(rotmat, np.array([0, 0, 1]))
        for p, color in ((x, 'red'), (y, 'blue'), (z, 'green')):
            # 只画z轴
            if color != 'green':
                continue
            # 向量起点、向量方向（以原点为起点时向量的终点）、箭头长度比例、箭身长度比例、颜色
            ax.quiver(tvec[0], tvec[1], tvec[2],
                      p[0], p[1], p[2],
                      arrow_length_ratio=0.2,
                      length=0.3 if color == 'green' else 0.2,  # z轴画的长一些
                      color=z_color)
        tvecs.append(tvec)


def show_poses_from_npy(npy):
    # 读取的从NeRF中保存的poses,shape为(num, 3, 5),num为照片数
    poses = np.load(npy)
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    plot_poses_NeRF(poses, 'green', ax)

    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_zlim(0, 5)
    plt.show()


def show_poses_from_npys(npys):
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    npys = npys.split()
    colors = ['g', 'r', 'b', 'c', 'm', 'y', 'k', 'w']
    for npy, color in zip(npys, colors):
        plot_poses_NeRF(np.load(npy), color, ax)

    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_zlim(0, 5)
    plt.show()
