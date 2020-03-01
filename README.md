# Team: ByU
2019 ICT 멘토링, 한이음

대전대학교 캡스톤 디자인

Project: Object Detection을 이용한 고객 맞춤형 광고 송출 모바일 로봇(Use MS Azure Face Recognition API and ROS)

Member: 김영기(Leader), 황의송, 류건희, 이병호

Professor: 유정기 교수님

Mentor: 김지영 멘토님(LG CNS)

한이음 제출 시연 동영상
https://www.youtube.com/watch?v=uk9DwQ39DXI
#

## ROBOT Design
![image](https://user-images.githubusercontent.com/47591345/61575355-8c631280-ab05-11e9-90cc-bf82d24123f8.png)

![image](https://user-images.githubusercontent.com/47591345/61575357-8ec56c80-ab05-11e9-9171-4bb98a8593ec.png)

![image](https://user-images.githubusercontent.com/47591345/61575358-908f3000-ab05-11e9-9f82-68f0aa7aebd4.png)
 
## 사용한 보드
* Odroid H2
* Arduino Mega2560

## Arduino에서 ROS를 사용하기 위한 라이브러리 설치
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

## 로봇 제어  
* robot control
      
      $rostopic pub -r 15 /byu_control geometry_msgs/Transform ‘[translation: [translation(x), 
      translation(y), translation(z)], rotation: [rotation(x), rotation(y), rotation(z), w]’
      
      <Example>
      $roscore
      $rosrun rosserial_python serial_node.py _port:=/dev/ttyACM0
      $rostopic pub -r 15 /byu_control geometry_msgs/Transform '{translation: [150, 150, 0], rotation: [0, 0, 0.5, 0]}'
