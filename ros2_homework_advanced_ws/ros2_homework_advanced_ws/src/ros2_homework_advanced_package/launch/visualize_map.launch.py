from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    bag_path = PathJoinSubstitution(
        [FindPackageShare('ros2_homework_advanced_package'), 'bag', 'map_to_visualize']
    )

    map_visualizer_node = Node(
        package='ros2_homework_advanced_package',
        executable='map_visualizer',
        name='map_visualizer',
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
    )

    play_bag = ExecuteProcess(
        cmd=['ros2', 'bag', 'play', bag_path, '--loop'],
        output='screen',
    )

    return LaunchDescription([
        map_visualizer_node,
        rviz_node,
        play_bag,
    ])