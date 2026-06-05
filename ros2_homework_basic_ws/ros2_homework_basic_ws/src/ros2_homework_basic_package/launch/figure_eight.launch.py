from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
    )

    eight_params_config = PathJoinSubstitution(
        [FindPackageShare('ros2_homework_basic_package'), 'config', 'eight_params.yaml']
    )

    figure_eight_node = Node(
        package='ros2_homework_basic_package',
        executable='figure_eight',
        name='figure_eight_node',
        output='screen',
        parameters=[eight_params_config],
    )

    return LaunchDescription([
        turtlesim_node,
        figure_eight_node,
    ])