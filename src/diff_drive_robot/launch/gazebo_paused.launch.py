from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Launch the robot in Gazebo with physics paused."""
    package_path = get_package_share_directory("diff_drive_robot")

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                f"{package_path}/launch/gazebo.launch.py"
            ),
            launch_arguments={"pause": "true"}.items()
        )
    ])
