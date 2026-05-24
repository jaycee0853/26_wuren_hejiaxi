# 机器学习作业

## 文件结构

```
homework/
├── README.md
├── 作业1/
│   ├── 作业1要求.txt
│   └── simulated_annealing_tsp.py
├── 作业2/
│   ├── 多元线性回归.ipynb
│   └── 岭回归.ipynb
├── 作业3/
│   └── SVM_iris分类.ipynb
└── 作业4/
    ├── Kmeans_Exp.ipynb
    └── cluster_dataset.mat
```

## 作业1：模拟退火算法

我选的算法是模拟退火，一开始完全不知道这是什么...

后来看了CSDN的博客才搞明白，就是模仿金属退火：温度高的时候接受差的解（跳出局部最优），温度降低后越来越只接受好的解。

参考资料：
https://blog.csdn.net/weixin_43484977/article/details/105029019
https://www.cnblogs.com/ranjiewen/p/6084052.html

踩坑记录：
一开始忘了TSP要回到起点，距离算错了debug了半天
一开始用随机交换两个城市做邻域操作，收敛很慢，后来换成2-opt好多了
copy的问题，直接改了原来的route导致结果不对...

运行结果：初始路径距离很大，模拟退火后明显降低了。收敛曲线前期下降快，后期变平。

## 作业2：多元线性回归

> *文件依赖说明*：`多元线性回归.ipynb` 和 `岭回归.ipynb` 共用加州房价数据集，岭回归其实就是在线性回归的基础上加了L2正则化，建议先看多元线性回归再看岭回归～

### 2a. 普通多元线性回归

用梯度下降训练，损失函数是均方误差。

关键公式：
预测：ŷ = Xw + b
损失：J = (1/2m) Σ(ŷ - y)²
梯度：w = w - α·(1/m)·Xᵀ(ŷ - y)

参考资料：
https://blog.csdn.net/qq_41871826/article/details/108171949

踩坑记录：
第一次没做标准化，梯度下降根本不收敛...不同特征量级差太大
梯度公式推了好几遍才推对

### 2b. 岭回归

在普通线性回归基础上加了L2正则化，防止过拟合。

关键公式：
损失：J = (1/2m) Σ(ŷ - y)² + (λ/2m) Σwⱼ²
梯度：w = w - α·[(1/m)·Xᵀ(ŷ - y) + (λ/m)·w]

参考资料：
https://blog.csdn.net/weixin_44612117/article/details/114260448

踩坑记录：
一开始把b也正则化了，效果很差，后来问AI才知道b不应该正则化
lambda太大确实会欠拟合

## 作业3：SVM分类

SVM就是找最大间隔超平面来分类。

实验内容：
1. 对比4种核函数（linear, poly, rbf, sigmoid）
2. 画不同核函数的决策边界
3. 看C和gamma对RBF核的影响

心得：
Iris数据集比较好分，各核函数效果都不错
RBF核效果最好
sigmoid核效果最差，不太适合这个数据集
标准化对SVM很重要
核函数那部分让AI帮我解释了一下，大概知道是怎么回事但数学推导还是有点懵

参考资料：
- https://blog.csdn.net/v_JULY_v/article/details/7624837
- https://scikit-learn.org/stable/modules/svm.html

## 作业4：K-Means聚类

> **文件依赖说明**：`Kmeans_Exp.ipynb` 依赖同目录下的 `cluster_dataset.mat` 数据文件，运行前需确保该文件存在

K-Means就是不断把点分到最近的中心，然后更新中心

步骤：
1. 随机选k个中心
2. 把每个点分到最近的中心
3. 更新中心为簇内点的均值
4. 重复2-3直到中心不变

心得：
看散点图数据大概分3簇
肘部法则在k=3处有拐点，验证了k=3
每次运行结果不太一样，因为初始中心是随机的

参考资料：
https://blog.csdn.net/qq_41871826/article/details/108171949
https://blog.csdn.net/weixin_43484977/article/details/105029019

## 运行环境

- Python 3.12
- numpy, matplotlib, scipy, scikit-learn

## 说明

写作业的时候用AI帮我解释了一些不太懂的概念（比如模拟退火的接受概率公式、岭回归为什么b不参与正则化），但代码都是自己理解之后写的，有AI检查
