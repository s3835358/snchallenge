#!/usr/bin/env python  

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

from std_msgs.msg import String

import geometry_msgs.msg
import tf2_geometry_msgs
import tf2_ros


class NavigationPath(Node):
    def __init__(self):
        super().__init__('aiil_navigationpath')
        
        # Define Parameters
        self.declare_parameters(
            namespace='',
            parameters=[
                ('frequency', 1.0)
            ]
        )
        
        # Look-up parameters values
        self.frequency = self.get_parameter('frequency').value
        
        # Publisher
        self.topic = "/path"
        self.pub = self.create_publisher(Path, self.topic, 10)
        
        # Transform listener
        self.tf_buffer = tf2_ros.buffer.Buffer()
        self.tf_listener = tf2_ros.transform_listener.TransformListener(self.tf_buffer, self)

        #initialise path message
        self.path_msg = Path()

        # Iteration
        self.timer = self.create_timer(self.frequency, self.publish_path)

        
    def publish_path(self):

        try:
            # Delay of 0.4 seconds allows for retrieval of transform  
            time = self.get_clock().now() - rclpy.duration.Duration(seconds=0.4)
            dest = 'map'
            src = 'base_link'

            # Create a new Path message
            
            self.path_msg.header.frame_id = src
            self.path_msg.header.stamp = time.to_msg()

            # Add one pose to the path (to-do: need to add all)
            
            pose = PoseStamped()
            pose.header.frame_id = src
            pose.header.stamp = time.to_msg()
            
            # We consider the position of base_link to be center of robot
            pose.pose.position.x = 0.0
            pose.pose.position.y = 0.0
            pose.pose.position.z = 0.0
            
            # Equivalent to 0,0,0 (roll, pitch, yaw)
            pose.pose.orientation.x = 1.0
            pose.pose.orientation.y = 0.0
            pose.pose.orientation.z = 0.0
            pose.pose.orientation.w = 0.0

            # Timeout for transform data
            timeout = rclpy.duration.Duration(seconds=0.8)

            poseT = self.tf_buffer.transform(pose, dest)

            self.path_msg.poses.append(poseT)

            # Publish the path
            self.pub.publish(self.path_msg)

        except tf2_ros.ExtrapolationException as ex:
            self.get_logger().info(f'Could not gain current data for {src} to {dest}: {ex}')

        except tf2_ros.TransformException as ex2:
            self.get_logger().info(f'Could not transform {src} to {dest}: {ex2}')

def main():
    rclpy.init()
    node = NavigationPath()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()
    exit(0)
