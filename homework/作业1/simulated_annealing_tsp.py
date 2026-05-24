"""
模拟退火算法求解TSP问题

一开始看到这个作业我完全不知道模拟退火是什么...
后来看了CSDN上的一篇博客才大概理解了：
https://blog.csdn.net/weixin_43484977/article/details/105029019

还有这个也看了，讲得比较详细：
https://www.cnblogs.com/ranjiewen/p/6084052.html

简单说就是模仿金属退火的过程：
- 温度高的时候，即使新解更差也有一定概率接受（这样能跳出局部最优）
- 温度慢慢降低，接受差解的概率越来越小
- 最后就收敛到最优解了

核心公式：如果新解更差，接受概率 P = exp(-ΔE / T)
这个公式我一开始没理解，让AI帮我解释了一下才搞懂：
  ΔE越大（差得越多），概率越小 → 合理，太差的解不太想接受
  T越大（温度越高），概率越大 → 合理，高温时应该多探索

一开始我写的版本bug很多，比如忘了TSP要回到起点，路径距离算错了...
下面是改了好几遍之后的版本
"""

import numpy as np
import matplotlib.pyplot as plt
import random
import math


def generate_cities(n, seed=42):
    """
    生成n个城市的坐标
    加了seed让每次运行结果一样，不然每次调试结果都不一样很难排查bug
    
    运作流程：
        1. 设随机种子
        2. 循环n次，每次随机生成一个(x,y)坐标
        3. 返回坐标列表
    
    重要变量：
        - n: 城市数量（局部变量）
        - coords: 城市坐标列表，每个元素是(x,y)（局部变量）
    """
    np.random.seed(seed)
    coords = []
    for i in range(n):
        x = np.random.uniform(0, 100)
        y = np.random.uniform(0, 100)
        coords.append((x, y))
    return coords


def compute_distance_matrix(coords):
    """
    算每两个城市之间的距离，存成矩阵
    我一开始想用列表存，后来发现矩阵查起来更方便
    
    运作流程：
        1. 看有多少个城市
        2. 建n*n的零矩阵
        3. 两层for循环算每对城市的欧氏距离
        4. 返回距离矩阵
    
    重要变量：
        - n: 城市数量（局部变量）
        - dist_matrix: 距离矩阵，dist_matrix[i][j]就是城市i到城市j的距离（局部变量）
    
    依赖关系：无
    """
    n = len(coords)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            dist_matrix[i][j] = math.sqrt(dx**2 + dy**2)
    return dist_matrix


def total_distance(route, dist_matrix):
    """
    算一条路径的总距离
    注意！！TSP是闭合回路，最后要回到起点！
    我第一次写的时候忘了这个，结果距离总是比别人的短一截，debug了半天才发现...
    
    运作流程：
        1. 遍历路径中相邻的城市对，把距离加起来
        2. 别忘了加上最后一个城市到起点的距离！
        3. 返回总距离
    
    重要变量：
        - route: 路径，比如[0,3,1,2,4]表示访问顺序（局部变量）
        - dist: 累加的总距离（局部变量）
    
    依赖关系：需要compute_distance_matrix算出来的距离矩阵
    """
    n = len(route)
    dist = 0.0
    for i in range(n - 1):
        dist = dist + dist_matrix[route[i]][route[i+1]]
    # 最后要回到起点！我第一次忘了这行...
    dist = dist + dist_matrix[route[-1]][route[0]]
    return dist


def generate_neighbor(route):
    """
    从当前路径生成一个新路径
    我用的是2-opt交换：随机选一段路径反转
    比如路径[0,1,2,3,4,5]，选i=1,j=4，就变成[0,4,3,2,1,5]
    
    一开始我试过直接随机交换两个城市，但效果不好，收敛很慢
    看了博客说2-opt效果更好，试了一下确实如此
    （2-opt这个名字也是问AI才知道的...）
    
    运作流程：
        1. 复制当前路径（不能直接改原来的！）
        2. 随机选两个位置i和j
        3. 把i到j之间的部分反转
        4. 返回新路径
    
    重要变量：
        - new_route: 新路径（局部变量）
        - i, j: 随机选的两个位置（局部变量）
    
    依赖关系：无
    """
    n = len(route)
    new_route = route.copy()  # 一定要copy！不然会改到原来的route
    i = random.randint(0, n-1)
    j = random.randint(0, n-1)
    if i > j:
        # 保证i < j，不然反转的范围会乱
        temp = i
        i = j
        j = temp
    # 反转i到j之间的部分
    part = new_route[i:j+1]
    part.reverse()
    new_route[i:j+1] = part
    return new_route


def simulated_annealing(coords, T_init=10000, T_end=1e-8, alpha=0.995, max_iter=1000):
    """
    模拟退火主函数
    
    运作流程：
        1. 算距离矩阵，随机生成初始路径
        2. 外层循环：温度不断降低（T = T * alpha）
        3. 内层循环：每个温度下尝试max_iter次扰动
           - 生成新路径
           - 如果新路径更短 → 直接接受
           - 如果新路径更长 → 以概率exp(-ΔE/T)接受
        4. 记录每次降温时的最优距离
        5. 返回最优路径、最优距离、历史记录
    
    重要变量：
        - T_init: 初始温度，设高一点让前期多探索
        - T_end: 终止温度
        - alpha: 降温系数，越接近1降温越慢（但迭代次数也更多）
        - max_iter: 每个温度迭代几次
        - current_route / current_dist: 当前路径和距离（局部变量）
        - best_route / best_dist: 历史最优（局部变量）
        - T: 当前温度（局部变量）
        - delta_E: 新解和当前解的差值（新-旧）（局部变量）
        - history: 记录收敛过程（局部变量）
        注：这个函数没有用全局变量，所有数据都通过参数传入
    
    依赖关系：
        - compute_distance_matrix() 算距离矩阵
        - total_distance() 算路径距离
        - generate_neighbor() 生成新路径
    """
    dist_matrix = compute_distance_matrix(coords)
    n = len(coords)

    # 随机生成初始路径
    current_route = list(range(n))
    random.shuffle(current_route)
    current_dist = total_distance(current_route, dist_matrix)

    # 记录最优解
    best_route = current_route.copy()
    best_dist = current_dist

    T = T_init
    history = []

    while T > T_end:
        for _ in range(max_iter):
            # 生成新路径
            new_route = generate_neighbor(current_route)
            new_dist = total_distance(new_route, dist_matrix)
            delta_E = new_dist - current_dist

            if delta_E < 0:
                # 新解更好，直接接受
                current_route = new_route
                current_dist = new_dist
            else:
                # 新解更差，以一定概率接受
                # 温度高→概率大→多探索  温度低→概率小→多利用
                prob = math.exp(-delta_E / T)
                if random.random() < prob:
                    current_route = new_route
                    current_dist = new_dist

            # 更新全局最优
            if current_dist < best_dist:
                best_route = current_route.copy()
                best_dist = current_dist

        history.append(best_dist)
        T = T * alpha  # 降温

    return best_route, best_dist, history


def plot_route(coords, route, title="路径"):
    """
    画TSP的路径图
    
    运作流程：
        1. 按路径顺序取出每个城市的坐标
        2. 加上起点的坐标（闭合回路）
        3. 画线和点，标上城市编号
    
    重要变量：
        - x_list, y_list: 路径上城市的x和y坐标
    
    依赖关系：无
    """
    x_list = []
    y_list = []
    for city in route:
        x_list.append(coords[city][0])
        y_list.append(coords[city][1])
    # 闭合回路
    x_list.append(coords[route[0]][0])
    y_list.append(coords[route[0]][1])

    plt.figure(figsize=(8, 6))
    plt.plot(x_list, y_list, 'o-', markersize=6, linewidth=1.5)
    for i, city in enumerate(route):
        plt.annotate(str(city), (coords[city][0], coords[city][1]),
                     textcoords="offset points", xytext=(5, 5), fontsize=8)
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True, alpha=0.3)
    plt.show()


def plot_convergence(history):
    """
    画收敛曲线
    可以看到距离是怎么慢慢降低的
    
    运作流程：
        1. 横轴迭代次数，纵轴最优距离
        2. 如果曲线最后变平了说明收敛了
    
    重要变量：
        - history: 每次降温记录的最优距离
    
    依赖关系：需要simulated_annealing返回的history
    """
    plt.figure(figsize=(8, 5))
    plt.plot(range(len(history)), history, 'b-', linewidth=1.5)
    plt.xlabel("迭代次数")
    plt.ylabel("最短路径距离")
    plt.title("模拟退火收敛曲线")
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    num_cities = 20

    print("模拟退火算法求解TSP问题")
    print("-" * 30)

    coords = generate_cities(num_cities)
    print(f"生成了{num_cities}个城市")

    dist_matrix = compute_distance_matrix(coords)

    # 算一下初始随机路径的距离
    init_route = list(range(num_cities))
    random.shuffle(init_route)
    init_dist = total_distance(init_route, dist_matrix)
    print(f"初始随机路径距离: {init_dist:.2f}")

    print("\n开始模拟退火搜索...")
    best_route, best_dist, history = simulated_annealing(
        coords, T_init=10000, T_end=1e-8, alpha=0.995, max_iter=100
    )

    print(f"最优路径距离: {best_dist:.2f}")
    print(f"比初始路径优化了: {(init_dist - best_dist) / init_dist * 100:.1f}%")
    print(f"最优路径: {best_route}")

    plot_route(coords, init_route, title=f"初始随机路径 (距离: {init_dist:.2f})")
    plot_route(coords, best_route, title=f"模拟退火最优路径 (距离: {best_dist:.2f})")
    plot_convergence(history)
