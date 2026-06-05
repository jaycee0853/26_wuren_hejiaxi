/*
  基础作业：控制turtlesim中的乌龟做八字形运动
  
  八字形 = 先画一个圆，再反方向画另一个圆
  两个圆在起点相切，连起来就是八字
  
  乌龟要画圆，需要同时给线速度(linear.x)和角速度(angular.z)
  画完一个圆的时间 = 2π / angular_velocity
  到时间后把angular.z取反就能换方向
  
  话题是 /turtle1/cmd_vel，turtlesim默认听这个
  消息类型是 geometry_msgs/msg/Twist
*/

#include <chrono>
#include <cmath>
#include <functional>
#include <memory>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class FigureEight : public rclcpp::Node
{
public:
  FigureEight()
  : Node("figure_eight_node")
  {
    // 声明两个参数，yaml里可以改，不用重编译
    this->declare_parameter<double>("linear_velocity", 2.0);
    this->declare_parameter<double>("angular_velocity", 1.0);

    // 发布方，往/turtle1/cmd_vel发消息控制乌龟
    publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("/turtle1/cmd_vel", 10);

    // 算一下画一个圆要多久
    // 周期T = 2π/ω，到点就翻
    double angular_velocity = this->get_parameter("angular_velocity").as_double();
    double circle_period = 2.0 * M_PI / angular_velocity;
    int circle_period_ms = static_cast<int>(circle_period * 1000);

    // 定时器1，每100ms发一次速度
    timer_ = this->create_wall_timer(
      std::chrono::milliseconds(100),
      std::bind(&FigureEight::publish_command, this));

    // 定时器2，每画完一个圆翻方向
    switch_timer_ = this->create_wall_timer(
      std::chrono::milliseconds(circle_period_ms),
      std::bind(&FigureEight::switch_direction, this));

    RCLCPP_INFO(this->get_logger(),
      "八字形运动启动: linear_velocity=%.2f, angular_velocity=%.2f, circle_period=%.2fs",
      this->get_parameter("linear_velocity").as_double(),
      angular_velocity,
      circle_period);
  }

private:
  void publish_command()
  {
    geometry_msgs::msg::Twist msg;
    double linear_velocity = this->get_parameter("linear_velocity").as_double();
    double angular_velocity = this->get_parameter("angular_velocity").as_double();

    // Twist有6个字段，但乌龟只用到linear.x和angular.z
    // direction_=1逆时针，-1顺时针
    msg.linear.x = linear_velocity;
    msg.linear.y = 0.0;
    msg.linear.z = 0.0;
    msg.angular.x = 0.0;
    msg.angular.y = 0.0;
    msg.angular.z = direction_ * angular_velocity;

    publisher_->publish(msg);
  }

  // 翻转方向：1变-1，-1变1
  void switch_direction()
  {
    direction_ = -direction_;
    RCLCPP_INFO(this->get_logger(),
      "切换方向: angular.z = %.2f", direction_ * this->get_parameter("angular_velocity").as_double());
  }

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::TimerBase::SharedPtr switch_timer_;
  int direction_ = 1;  // 1逆时针，-1顺时针
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<FigureEight>());
  rclcpp::shutdown();
  return 0;
}
