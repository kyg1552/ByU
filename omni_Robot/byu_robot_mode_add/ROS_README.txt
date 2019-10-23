

roscore

rosrun rosserial_python serial_node.py /dev/ttyACM0

rosrun byu_robot byu_ultrasensor

rostopic pub -r 10 /byu_control geometry_msgs/Transform '{translation: {x: 0.0, y: 0.0, z: 0.0}, rotation: {x: 0.0, y: 0.0, z: 0.0, w: 0.0}}'

rostopic pub -r 10 /byu_control geometry_msgs/Transform '{translation: {x: 100.0, y: 150.0, z: 0.0}, rotation: {x: 0.0, y: 0.0, z: 0.5, w: 0.0}}'

