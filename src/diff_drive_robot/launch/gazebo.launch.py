import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    package_name = "diff_drive_robot"

    pkg_path = get_package_share_directory(package_name)

    xacro_file = os.path.join(
        pkg_path,
        "urdf",
        "diff_drive_robot.xacro"
    )

    gazebo_ros_path = get_package_share_directory("gazebo_ros")

    # Convert Xacro -> URDF
    robot_description = ParameterValue(
        Command(["xacro ", xacro_file]),
        value_type=str
    )

    # Start Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                gazebo_ros_path,
                "launch",
                "gazebo.launch.py"
            )
        ),
        launch_arguments={
            "pause": LaunchConfiguration("pause")
        }.items()
    )

    # Publish robot TF
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description
            }
        ]
    )

    # Spawn robot into Gazebo
    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-topic",
            "robot_description",
            "-entity",
            "diff_drive_robot",
            "-z",
            "0.5"
        ],
        output="screen"
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "pause",
            default_value="false",
            description="Start Gazebo with physics paused."
        ),
        gazebo,
        robot_state_publisher,
        spawn_robot
    ])
