#include "ros/ros.h"
#include "std_msgs/String.h"
#include "sensor_msgs/Range.h"

void ultraCallback1(const sensor_msgs::Range &range_msg1)
{
  ROS_INFO("distance_F:[%f]", range_msg1.range);
}
void ultraCallback2(const sensor_msgs::Range &range_msg2)
{
  ROS_INFO("distance_L:[%f]", range_msg2.range);
}
void ultraCallback3(const sensor_msgs::Range &range_msg3)
{
  ROS_INFO("distance_R:[%f]", range_msg3.range);
}
void ultraCallback4(const sensor_msgs::Range &range_msg4)
{
  ROS_INFO("distance_Side_L:[%f]", range_msg4.range);
}
void ultraCallback5(const sensor_msgs::Range &range_msg5)
{
  ROS_INFO("distance_Side_R:[%f]", range_msg5.range);
}


int main(int argc, char **argv)
{
  
  ros::init(argc, argv, "byu_ultrasensor");
 
  ros::NodeHandle nh;

  ros::Subscriber sub1 = nh.subscribe("/distance_F", 1, ultraCallback1);
  ros::Subscriber sub2 = nh.subscribe("/distance_L", 1, ultraCallback2);
  ros::Subscriber sub3 = nh.subscribe("/distance_R", 1, ultraCallback3);
  ros::Subscriber sub4 = nh.subscribe("/distance_Side_L", 1, ultraCallback4);
  ros::Subscriber sub5 = nh.subscribe("/distance_Side_R", 1, ultraCallback5);

  ros::spin();

  return 0;
}

