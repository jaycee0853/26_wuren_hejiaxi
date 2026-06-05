/*
  进阶作业：订阅/estimation/slam/map，把锥桶变成Marker显示在RViz里
  
  bag回放的时候会自动往/estimation/slam/map发Map消息
  Map里有四种锥桶：黄、蓝、红、未知
  每个锥桶有position(x,y,z)这些字段
  我把它们转成Marker发出去，RViz就能看见了
  
  一开始坐标系搞不明白，后来发现Map消息的header里有frame_id
  如果header里没有就默认用"map"
  RViz的Fixed Frame要跟消息里的frame_id对上，不然看不见
  
  订阅：fsd_common_msgs/msg/Map
  发布：visualization_msgs/msg/MarkerArray（一次发一堆Marker比较方便）
*/

#include <functional>
#include <memory>
#include <string>
#include <vector>

#include "fsd_common_msgs/msg/map.hpp"
#include "rclcpp/rclcpp.hpp"
#include "visualization_msgs/msg/marker.hpp"
#include "visualization_msgs/msg/marker_array.hpp"

class MapVisualizer : public rclcpp::Node
{
public:
  MapVisualizer()
  : Node("map_visualizer")
  {
    // 默认坐标系map，消息里有frame_id就用消息里的
    this->declare_parameter<std::string>("frame_id", "map");

    // 订阅地图话题
    sub_map_ = this->create_subscription<fsd_common_msgs::msg::Map>(
      "/estimation/slam/map",
      10,
      std::bind(&MapVisualizer::map_callback, this, std::placeholders::_1));

    // 发布MarkerArray，RViz显示锥桶
    marker_pub_ = this->create_publisher<visualization_msgs::msg::MarkerArray>("cone_markers", 10);
  }

private:
  void map_callback(const fsd_common_msgs::msg::Map::SharedPtr msg)
  {
    visualization_msgs::msg::MarkerArray marker_array;

    // 从消息header拿坐标系，没有就用默认值
    // 这个地方卡了我挺久，一开始Fixed Frame没设对导致Marker不显示
    std::string frame_id = msg->header.frame_id;
    if (frame_id.empty()) {
      frame_id = this->get_parameter("frame_id").as_string();
    }

    int marker_id = 0;

    // 四种锥桶，颜色分开
    add_cone_markers(marker_array, msg->cone_yellow, frame_id, marker_id, 1.0f, 1.0f, 0.0f, "yellow");
    add_cone_markers(marker_array, msg->cone_blue,   frame_id, marker_id, 0.0f, 0.0f, 1.0f, "blue");
    add_cone_markers(marker_array, msg->cone_red,    frame_id, marker_id, 1.0f, 0.0f, 0.0f, "red");
    add_cone_markers(marker_array, msg->cone_unknown,frame_id, marker_id, 0.3f, 0.3f, 0.3f, "unknown");

    marker_pub_->publish(marker_array);
  }

  // 把一组锥桶转成Marker添加到marker_array里
  void add_cone_markers(
    visualization_msgs::msg::MarkerArray & marker_array,
    const std::vector<fsd_common_msgs::msg::Cone> & cones,
    const std::string & frame_id,
    int & marker_id,
    float r, float g, float b,
    const std::string & ns)
  {
    int counter = 0;
    for (const auto & cone : cones) {
      visualization_msgs::msg::Marker marker;

      // frame_id和stamp，要跟RViz对上
      marker.header.frame_id = frame_id;
      marker.header.stamp = this->now();

      // ns和id用来区分Marker
      // 同一个ns+id会更新，不会重复加
      marker.ns = "cones/" + ns;
      marker.id = counter;

      // ADD是添加/更新，CYLINDER是圆柱体
      marker.action = visualization_msgs::msg::Marker::ADD;
      marker.type = visualization_msgs::msg::Marker::CYLINDER;

      // 位置用锥桶的坐标
      auto & pos = cone.position;
      marker.pose.position.x = pos.x;
      marker.pose.position.y = pos.y;
      marker.pose.position.z = pos.z;
      marker.pose.orientation.w = 1.0;

      // scale.x和y是底面半径，z是高度
      marker.scale.x = 0.3;
      marker.scale.y = 0.3;
      marker.scale.z = 0.5;

      // 颜色，a>0不然看不见
      marker.color.r = r;
      marker.color.g = g;
      marker.color.b = b;
      marker.color.a = 0.8f;

      // 0.5秒后消失，不然会一直叠加
      marker.lifetime = rclcpp::Duration::from_seconds(0.5);

      marker_array.markers.push_back(marker);
      ++counter;
    }
    marker_id += counter;
  }

  rclcpp::Subscription<fsd_common_msgs::msg::Map>::SharedPtr sub_map_;
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_pub_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MapVisualizer>());
  rclcpp::shutdown();
  return 0;
}
