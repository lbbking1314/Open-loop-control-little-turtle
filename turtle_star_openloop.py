#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROS开环轨迹控制：小海龟走正五角星（无反馈，纯时序控制）
"""

import rospy
from geometry_msgs.msg import Twist
import math


def turtle_star_controller():
    # 1. 初始化ROS节点（开环控制节点）
    rospy.init_node('turtle_star_openloop_controller', anonymous=True)

    # 2. 创建发布者：发布速度指令到/turtle1/cmd_vel话题
    vel_pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)

    # 3. 设置循环频率（控制指令发布频率，Hz）
    loop_rate = rospy.Rate(10)  # 10Hz，每0.1秒发布一次指令

    # 4. 初始化Twist消息（速度指令载体）
    vel_msg = Twist()

    # ========== 开环控制核心参数（可调整） ==========
    linear_speed = 0.8  # 直行线速度 (m/s)
    angular_speed = 1.0  # 转向角速度 (rad/s)
    side_duration = 2.5  # 每条边直行时间 (秒)
    turn_angle = 144  # 正五角星每次转向角度 (°)
    turn_rad = math.radians(turn_angle)  # 转换为弧度
    turn_duration = turn_rad / angular_speed  # 转向所需时间

    rospy.loginfo("开环控制启动：小海龟将走正五角星 🎇")
    rospy.loginfo(f"参数：线速度={linear_speed}m/s，转向角度={turn_angle}°，转向时间={turn_duration:.2f}s")

    try:
        # 开环循环：重复5次「直行+转向」（五角星5条边）
        for _ in range(5):
            # 阶段1：直行（走五角星的一条边）
            vel_msg.linear.x = linear_speed  # 仅x轴直行
            vel_msg.angular.z = 0.0  # 角速度为0，不转向
            rospy.loginfo("→ 直行中...")
            start_time = rospy.Time.now()
            # 开环时间控制：固定时间内持续发布直行指令
            while (rospy.Time.now() - start_time).to_sec() < side_duration:
                vel_pub.publish(vel_msg)
                loop_rate.sleep()  # 保证发布频率稳定

            # 阶段2：转向（144°，开环时间控制）
            vel_msg.linear.x = 0.0  # 停止直行
            vel_msg.angular.z = angular_speed  # 设定转向角速度
            rospy.loginfo("🔄 转向中...")
            start_time = rospy.Time.now()
            # 开环时间控制：固定时间内持续发布转向指令
            while (rospy.Time.now() - start_time).to_sec() < turn_duration:
                vel_pub.publish(vel_msg)
                loop_rate.sleep()

        # 5. 完成轨迹后停止运动
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0.0
        vel_pub.publish(vel_msg)
        rospy.loginfo("✅ 正五角星轨迹完成，小海龟已停止")

    except rospy.ROSInterruptException:
        # 捕获节点中断异常，确保小海龟停止
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0.0
        vel_pub.publish(vel_msg)
        rospy.logwarn("⚠️ 节点被中断，小海龟已紧急停止")


if __name__ == '__main__':
    try:
        turtle_star_controller()
    except rospy.ROSInterruptException:
        pass
