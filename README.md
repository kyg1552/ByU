# Team: ByU

Project: Open-source robot platform providing personalized advertisements

#
## ROBOT H/W Architecture
![HW구성도](https://user-images.githubusercontent.com/37207332/75628129-6c5a0c80-5c19-11ea-8be5-8316deee991d.JPG)

## ROBOT Design
![image](https://user-images.githubusercontent.com/47591345/61575355-8c631280-ab05-11e9-90cc-bf82d24123f8.png)

![image](https://user-images.githubusercontent.com/47591345/61575357-8ec56c80-ab05-11e9-9171-4bb98a8593ec.png)

![image](https://user-images.githubusercontent.com/47591345/61575358-908f3000-ab05-11e9-9f82-68f0aa7aebd4.png)
 
## Used Embedded board
* Odroid H2
* Arduino Mega2560

## ROS Libarary install on Arduino
* rosserial install for Arduino
   * http://wiki.ros.org/rosserial_arduino/Tutorials/Arduino%20IDE%20Setup
   * Arduino IDE Setup
            
            $sudo apt-get install ros-kinetic-rosserial-arduino
            $sudo apt-get install ros-kinetic-rosserial
    
   * Installing from Source onto the ROS workstation

          $cd ~/catkin_ws/src
          $git clone https://github.com/ros-drivers/rosserial.git
          $cd ~/catkin_ws && catkin_make
    
   * Install ros_lib into the Arduino Environment
    
         $cd ~/Arduino/libraries
         $rm -rf ros_lib
         $rosrun rosserial_arduino make_libraries.py .

* Start ROS Master & rosserial
      
         $roscore
         $rosrun rosserial_python serial_node.py _port:=/dev/ttyACM0

## How to Robot control

1. byu_robot_mode_add.ino file upload on Arduino Mega

2. connect Arduino Mega and odroid H2(Master) to rosserial
   
      * rosrun rosserial_python serial_node.py _port:=/dev/serial_port_file(=ttyACM#,#:serial_port_number)

3. robot control ros command

       $rostopic pub -r 15 /byu_control geometry_msgs/Transform ‘[translation: [translation(x),translation(y), translation(z)], rotation: [rotation(x), rotation(y), rotation(z), w]’
4. Example
    
       $roscore
       $rosrun rosserial_python serial_node.py _port:=/dev/ttyACM0
       $rostopic pub -r 15 /byu_control geometry_msgs/Transform '{translation: [150, 150, 0], rotation: [0, 0, 0.5, 1.0]}'
