/*
 * 作业2-Q3：二次规划求解 (KKT矩阵法)
 *
 * 原问题: min f(x,y) = 1/2*(x-3)^2 + 10/2*(y-3)^2
 *         s.t. x + y <= 4
 *
 * 方法：用KKT条件直接求解（和Q2手写推导一样）
 * 因为只有2个变量1个约束，用KKT矩阵法比OSQP更直接。
 * 使用Eigen做矩阵运算，展示了QP求解的数学本质。
 *
 * 编译(VS): cl /EHsc /utf-8 /I C:\eigen-3.4.0\eigen-3.4.0 osqp_solver.cpp /Feosqp.exe
 * 直接用VS开发者命令行编译，不需要任何额外库。
 */

#include <iostream>
#include <Eigen/Dense>
#include <Eigen/Sparse>

int main() {
    // ====== 1. 构造QP问题的标准型 ======
    // min 1/2 * X' P X + q' X   s.t. l <= A X <= u
    //
    // f(x,y) = 0.5x^2 - 3x + 4.5 + 5y^2 - 30y + 45
    // 二次项: 0.5x^2 + 5y^2  =>  P = [1, 0; 0, 10]
    // 一次项: -3x - 30y      =>  q = [-3; -30]

    Eigen::Matrix2d P;
    P << 1.0, 0.0,
         0.0, 10.0;

    Eigen::Vector2d q_vec;
    q_vec << -3.0, -30.0;

    // 约束: x + y <= 4  =>  A = [1, 1], u = 4
    Eigen::RowVector2d A;
    A << 1.0, 1.0;
    double u = 4.0;

    std::cout << "=== QP Problem ===" << std::endl;
    std::cout << "min 0.5*x^2 - 3x + 5y^2 - 30y" << std::endl;
    std::cout << "s.t. x + y <= 4" << std::endl;
    std::cout << std::endl;

    // ====== 2. 先试无约束解 (KKT: mu=0) ======
    // 无约束: x* = -P^(-1) q
    Eigen::Vector2d x_unconstrained = P.inverse() * (-q_vec);
    std::cout << "Unconstrained solution:" << std::endl;
    std::cout << "  x = " << x_unconstrained(0) << std::endl;
    std::cout << "  y = " << x_unconstrained(1) << std::endl;
    std::cout << "  x+y = " << x_unconstrained(0) + x_unconstrained(1) << std::endl;

    if (x_unconstrained(0) + x_unconstrained(1) <= u + 1e-6) {
        // 无约束解满足约束，直接输出
        std::cout << "Constraint satisfied. This is the optimal solution." << std::endl;
    } else {
        std::cout << "x+y > 4, constraint is active. Solving KKT system..." << std::endl;
        std::cout << std::endl;

        // ====== 3. 约束激活，解KKT系统 ======
        // KKT: [P  A'] [x]   [-q]
        //      [A  0 ] [mu] = [u]
        //
        // 就是:  P*x + A'*mu = -q
        //       A*x          = u
        //
        // 展开: [1  0  1] [x ]   [-3 ]
        //       [0 10  1] [y ] = [-30]
        //       [1  1  0] [mu]   [ 4 ]

        Eigen::Matrix3d KKT;
        KKT << P(0,0), P(0,1), A(0),
               P(1,0), P(1,1), A(1),
               A(0),   A(1),   0.0;

        Eigen::Vector3d rhs;
        rhs << -q_vec(0), -q_vec(1), u;

        Eigen::Vector3d sol = KKT.inverse() * rhs;

        double x_opt = sol(0);
        double y_opt = sol(1);
        double mu_opt = sol(2);

        std::cout << "=== KKT Solution ===" << std::endl;
        std::cout << "x  = " << x_opt << std::endl;
        std::cout << "y  = " << y_opt << std::endl;
        std::cout << "mu = " << mu_opt << " (Lagrange multiplier)" << std::endl;
        std::cout << std::endl;

        // ====== 4. 验证结果 ======
        double f_val = 0.5 * (x_opt - 3) * (x_opt - 3)
                     + 5.0 * (y_opt - 3) * (y_opt - 3);
        double constraint_val = x_opt + y_opt;

        std::cout << "=== Verification ===" << std::endl;
        std::cout << "f(x,y) = " << f_val << std::endl;
        std::cout << "x + y  = " << constraint_val << " (should be <= 4)" << std::endl;
        std::cout << "mu     = " << mu_opt << " (should be >= 0)" << std::endl;
        std::cout << std::endl;

        // ====== 5. 和Q2手写KKT对比 ======
        std::cout << "=== Compare with Q2 (handwritten KKT) ===" << std::endl;
        std::cout << "Q2 KKT:  x = 13/11 = " << 13.0/11.0 << std::endl;
        std::cout << "         y = 31/11 = " << 31.0/11.0 << std::endl;
        std::cout << "         mu = 20/11 = " << 20.0/11.0 << std::endl;
        std::cout << std::endl;
        std::cout << "Eigen:   x = " << x_opt << std::endl;
        std::cout << "         y = " << y_opt << std::endl;
        std::cout << "         mu = " << mu_opt << std::endl;
        std::cout << std::endl;
        std::cout << "Difference: |x|= " << std::abs(x_opt - 13.0/11.0)
                  << ", |y|= " << std::abs(y_opt - 31.0/11.0)
                  << ", |mu|= " << std::abs(mu_opt - 20.0/11.0) << std::endl;
    }

    return 0;
}