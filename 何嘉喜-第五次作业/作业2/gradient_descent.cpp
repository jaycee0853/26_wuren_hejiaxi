/*
 * 作业2-Q1：无约束寻优 —— 梯度下降法
 * 代价函数: f(x,y) = 1/2*(x-3)^2 + 10/2*(y-3)^2
 * 梯度: [x-3, 10*(y-3)]
 * 目标: 到达(3,3)附近，误差<1e-3
 *
 * 编译(VS): cl /EHsc /utf-8 /I eigen路径 gradient_descent.cpp /Fegd.exe
 */

#include <iostream>
#include <cmath>
#include <Eigen/Dense>

using namespace Eigen;

int main() {
    // 状态量 X = [x, y]，从(0,0)出发
    Vector2d X(0.0, 0.0);
    // 信号源在(3,3)
    Vector2d target(3.0, 3.0);

    // 梯度函数
    // y方向梯度是x方向的10倍，所以y走得更猛
    auto grad = [](const Vector2d& X) -> Vector2d {
        return Vector2d(X(0) - 3.0, 10.0 * (X(1) - 3.0));
    };

    // 试几个不同的学习率看看效果
    double lr_list[] = {0.01, 0.05, 0.1, 0.15};

    for (double eta : lr_list) {
        X = Vector2d(0.0, 0.0);  // 重置
        int iter = 0;
        int max_iter = 100000;  // 防止死循环

        while (iter < max_iter) {
            Vector2d g = grad(X);
            X = X - eta * g;  // 往梯度反方向走一步
            iter++;

            // 看看到了没
            if ((X - target).norm() < 1e-3) {
                break;
            }
        }

        double error = (X - target).norm();
        std::cout << "eta = " << eta
                  << " | iter = " << iter
                  << " | pos = (" << X(0) << ", " << X(1) << ")"
                  << " | err = " << error << std::endl;

        if (error >= 1e-3) {
            std::cout << "  -> not converged" << std::endl;
        }
    }

    return 0;
}
