cmake_minimum_required(VERSION 2.8.3)
project(byu_robot)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES byu_robot
#  CATKIN_DEPENDS roscpp rospy std_msgs
#  DEPENDS system_lib
)

include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)

add_executable(byu_ultrasensor src/ultrasensor.cpp)

target_link_libraries(byu_ultrasensor
   ${catkin_LIBRARIES}
)

