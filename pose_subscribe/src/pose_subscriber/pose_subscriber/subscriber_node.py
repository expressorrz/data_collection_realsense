#!/usr/bin/env python3
# filepath: /home/ipu/Documents/robot_learning/ICG_ROS2/src/pose_subscriber.py

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TwistStamped
from ros2_aruco_interfaces.msg import ArucoMarkers
from geometry_msgs.msg import PoseArray, Pose
import os

class Msg_Subscriber(Node):
    def __init__(self, save_path, run_id):
        super().__init__('twist_subscriber')

        self.save_path = save_path
        self.run_id = run_id

        self.marker_list = [0]
        topic_name = '/aruco_markers_eyeinhand'

        self.poses_data_dict = {}
        
        for marker_id in self.marker_list:
            self.poses_data_dict[f'pose_{marker_id}'] = []
        
        self.pose_subscription = self.create_subscription(
            ArucoMarkers,
            topic_name,
            self.pose_callback,
            10  # QoS
        )
    
    def pose_callback(self, msg):
        for marker_id in self.marker_list:
            if marker_id not in msg.marker_ids:
                continue
            else:
                # Get the index from marker_list and the pose from the message
                idx = msg.marker_ids.index(marker_id)
                self.get_logger().info(f'idx: {idx}, marker_ids: {msg.marker_ids}, marker_id: {marker_id}')

                if msg.poses[idx].position.x != 0.0:
                    

                    timestamp_sec = msg.header.stamp.sec
                    timestamp_nanosec = msg.header.stamp.nanosec
                    position = msg.poses[idx].position
                    orientation = msg.poses[idx].orientation
            
                    x = position.x
                    y = position.y
                    z = position.z
                    qx = orientation.x
                    qy = orientation.y
                    qz = orientation.z
                    qw = orientation.w
            
                    self.get_logger().info(
                        f'received object pose:\n'
                        f'position: x={x:.3f}, y={y:.3f}, z={z:.3f}\n'
                        f'orientation: x={qx:.3f}, y={qy:.3f}, z={qz:.3f}, w={qw:.3f}'
                    )

                    # Store the pose in the list
                    self.poses_data_dict[f'pose_{marker_id}'].append([timestamp_sec, timestamp_nanosec, x, y, z, qx, qy, qz, qw])
                else:
                    self.poses_data_dict[f'pose_{marker_id}'].append([0, 0, 0, 0, 0, 0, 0, 0, 0])
            
  
        
        # Save the list to an npz file
        np.savez(f'{self.save_path}/id_{self.run_id}.npz', **self.poses_data_dict)

def main(args=None):
    task_id = input("Task No.").strip()
    operator_id = input("Human No.").strip()
    run_id = input("ID No.").strip()

    save_path = f'./poses/task_{task_id}/op_{operator_id}/'
    os.makedirs(save_path, exist_ok=True)

    
    rclpy.init(args=args)
    msg_subscriber = Msg_Subscriber(save_path, run_id)

    
    try:
        rclpy.spin(msg_subscriber)
    except KeyboardInterrupt:
        print('User interrupted with Ctrl-C')
    finally:
        msg_subscriber.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()