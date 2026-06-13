%% 第二问：轨迹跟踪
clear; clc; close all

% 车辆参数
lfr = 2.168 + 1.907; % 轴距
dt = 0.01;
v = 15; 
sim_steps = 2000;

% 参考轨迹 (正弦曲线)
X_ref = 0:0.1:200; 
Y_ref = 10 * sin(X_ref / 15); 

% 纯跟踪参数
Ld = 5;  % 预瞄距离，3太小会晃，8太大反应慢，5还行

% 初始状态（故意偏了3米）
X = X_ref(1); Y = Y_ref(1) + 3; phi = 0;
X_vec = zeros(1, sim_steps); Y_vec = zeros(1, sim_steps);


for ii = 1:sim_steps
    X_vec(ii) = X; Y_vec(ii) = Y;

    % ================= TODO 2.1: 纯跟踪算法 =================
    % 找预瞄点：先找最近的参考点，再往前找距离>=Ld的点

    dx = X_ref - X;
    dy = Y_ref - Y;
    dist = sqrt(dx.^2 + dy.^2);

    [~, nearest_idx] = min(dist);  % 最近的参考点

    % 往前找第一个距离>=Ld的点当预瞄目标
    target_idx = nearest_idx;
    for jj = nearest_idx:length(X_ref)
        if dist(jj) >= Ld
            target_idx = jj;
            break;
        end
    end

    X_target = X_ref(target_idx);
    Y_target = Y_ref(target_idx);

    % 算目标点相对于车头的偏角
    dx_target = X_target - X;
    dy_target = Y_target - Y;
    alpha = atan2(dy_target, dx_target) - phi;

    % 纯跟踪公式求转向角
    sigma = atan2(2 * lfr * sin(alpha), Ld);

    % 别让转向角太离谱
    sigma = max(min(sigma, pi/4), -pi/4);

    % ================= TODO 2.2: 状态更新 =================
    % 复用第一问的运动学模型
    phi_dot = v / lfr * tan(sigma);
    phi = phi + phi_dot * dt;
    X = X + v * cos(phi) * dt;
    Y = Y + v * sin(phi) * dt;

    % 到终点了就停
    if X >= X_ref(end), break; end
end

% 画图对比
figure; hold on; grid on;
plot(X_vec(1:ii), Y_vec(1:ii), 'r-', 'LineWidth', 2);  % 先画实际轨迹
plot(X_ref, Y_ref, 'b--', 'LineWidth', 2);  % 再画参考轨迹，蓝色虚线
legend('实际行驶轨迹', '参考规划轨迹');
title(['Pure Pursuit 跟踪 (Ld = ', num2str(Ld), 'm)']);
xlabel('X [m]'); ylabel('Y [m]'); axis equal;
