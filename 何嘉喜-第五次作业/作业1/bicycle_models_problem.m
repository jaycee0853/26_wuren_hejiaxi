clear; clc; close all
%% 第一问：运动学自行车模型 (开环测试 - 必做)
% 车辆基础参数
lf = 2.168;
lr = 1.907;
lfr = lf + lr; % 轴距
sigma = 5 / 180 * pi; % 前轮转角5度
dt = 0.01; % 仿真步长
v = 30; % 车速 30 m/s

X = 1; Y = 10; phi = 0; % 初始状态
phi_vec = []; X_vec = []; Y_vec = [];

for ii = 1:5000
    phi_vec = [phi_vec, phi];
    X_vec = [X_vec, X + lr*cos(phi)]; % 记录质心位置
    Y_vec = [Y_vec, Y + lr*sin(phi)];

    % ================= TODO 1.1: 运动学模型状态更新 =================
    % 以后轴为参考点，横摆角速度 = v*tan(sigma)/L
    % 然后欧拉积分更新phi、X、Y

    phi_dot = v / lfr * tan(sigma);  % 横摆角速度
    phi = phi + phi_dot * dt;        % 先更新航向角
    X = X + v * cos(phi) * dt;      % 再更新位置
    Y = Y + v * sin(phi) * dt;
    % ===============================================================
end

figure(1); hold on; plot(X_vec, Y_vec, 'b.');
axis equal; title("Kinematic Bicycle Model");
xlabel("X [m]"); ylabel("Y [m]");


% %% =================================================================
% %% 拓展问题：动力学模型 (选做，我没做)
% %% =================================================================
% % 动力学模型考虑轮胎侧偏力，比运动学更真实
% 
% Iz = 5633.44; % 横摆转动惯量
% Cf = 100000;  % 前轮侧偏刚度
% Cr = 100000;  % 后轮侧偏刚度
% m = 1500;     % 车辆质量
% 
% X = 1; Y = 10; phi = 0; % 重置
% x_dot = v; y_dot = 0; phi_dot = 0;
% phi_vec = []; X_vec_dyn = []; Y_vec_dyn = [];
% 
% for ii = 1:5000
%     phi_vec = [phi_vec, phi];
%     X_vec_dyn = [X_vec_dyn, X];
%     Y_vec_dyn = [Y_vec_dyn, Y];
% 
%     % 前后轮侧偏角（已经给好的）
%     alpha_f = sigma - (y_dot + lf * phi_dot) / x_dot;
%     alpha_r = - (y_dot - lr * phi_dot) / x_dot;
% 
%     % ================= TODO 拓展: 动力学模型状态更新 =================
%     % 侧偏力 = 刚度 × 侧偏角
%     Fyf = Cf * alpha_f;  % 前轮横向力
%     Fyr = Cr * alpha_r;  % 后轮横向力
% 
%     % 牛顿第二定律
%     y_ddot = (Fyf * cos(sigma) + Fyr) / m;            % 横向加速度
%     phi_ddot = (lf * Fyf * cos(sigma) - lr * Fyr) / Iz;  % 横摆角加速度
% 
%     % 积分更新速度
%     y_dot = y_dot + y_ddot * dt;
%     phi_dot = phi_dot + phi_ddot * dt;
% 
%     % 车体坐标转全局坐标
%     phi = phi + phi_dot * dt;
%     X = X + (x_dot * cos(phi) - y_dot * sin(phi)) * dt;
%     Y = Y + (x_dot * sin(phi) + y_dot * cos(phi)) * dt;
% 
%     % ===============================================================
% end
% figure(1); hold on;
% plot(X_vec_dyn, Y_vec_dyn, 'r.');
% legend('Kinematic (运动学)', 'Dynamic (动力学)');
% title("Kinematic vs Dynamic Bicycle Model (v = 30m/s)");
