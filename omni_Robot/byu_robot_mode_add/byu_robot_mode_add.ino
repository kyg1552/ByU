/* Omni Motor Control ByU Robot

  작성자: 

  최종 수정일:
  참고자료: https://github.com/lupusorina/nexus-robots : NEXUS_ROBOT demo-code 및 Library
           https://simsamo.tistory.com/13?category=700958 : filter
           http://docs.ros.org/en/melodic/api/geometry_msgs/html/msg/Twist.html
           - Ultrasound Sensosr
            https://fleshandmachines.wordpress.com/2011/09/16/arduino-double-sonar-with-ros/ - 초음파센서 2개 이상 사용 시
            http://docs.ros.org/melodic/api/sensor_msgs/html/msg/Range.html  - 초음파 센서 값 ros type

  내용:
        모바일 플렛폼 3-omni wheel 제어
        초음파 센서 5개 이용 회피 알고리즘
        IR센서 이용 낙상 방지
        아두이노 전원 스위치, 모터 드라이버 릴레이 스위치
        ROS 연동해서 rostopic으로 로봇 translation x,translation y, rotation z 값 제어


  추가할 내용:
*/

/* 
 *  Omni Motor Control ByU Robot
 */

#define _NAMIKI_MOTOR
#include <MatrixMath.h>
#include <math.h>
#include <ros.h>
#include <geometry_msgs/Twist.h>

//Baudrate
#define BAUDRATE1 9600
#define BAUDRATE2 115200

// 초음파 pin 정의
#define TRIG_Front 24//정면 초음파 TRIG pin
#define ECHO_Front 25//정면 초음파 ECHO pin

#define TRIG_Left 26//좌측 초음파 TRIG pin
#define ECHO_Left 27//좌측 초음파 ECHO pin

#define TRIG_Right 28//우측 초음파 TRIG pin
#define ECHO_Right 29//우측 초음파 ECHO pin

#define TRIG_side_decay_rateL 30//좌측 측면 초음파 TRIG pin
#define ECHO_side_decay_rateL 31//좌측 측면 초음파 ECHO pin

#define TRIG_side_decay_rateR 32//우측 측면 초음파 TRIG pin
#define ECHO_side_decay_rateR 33//우측 측면 초음파 ECHO pin

// 초음파 측정 최대 거리: PulseIn함수에서 측정거리 over될 시 0을 반환
#define DIST_MAX 100 // DIST_MAX값까지만 측정 그 외에는 물체가 없다고 본다.
#define DIST_MIN 2 // 측정 최소 거리 지정
#define DIST_S (DIST_MAX *58.2) //초음파센서 타임아웃 설정 (최대거리)


// Motor Pin 정의부

// 뒷 바퀴 1번
#define BACK_PWM 13
#define BACK_DIR 12

// 왼쪽바퀴 2번
#define LEFT_PWM 9
#define LEFT_DIR 8

// 오른쪽 바퀴 3번
#define RIGHT_PWM 7
#define RIGHT_DIR 6

//모터드라이버 릴레이 핀
#define MOTOR_DRIVER_RELAY 37

//IR센서 핀
#define IR_SENSOR 40
bool IR_sensor_check = false;

// Omni Body 관련 정의부
#define NR_OMNIWHEELS 3 // 옴니휠 갯수
#define BODY_RADIUS  160 //mm 로봇 반지름
#define REDUCTION_RATIO_NAMIKI_MOTOR 80 //감속비
#define WHEEL_RADIUS  24 //바퀴 반지름
#define WHEEL_CIRC  (WHEEL_RADIUS * 2 * M_PI) //M_PI는 math.h에 있는 pi값. 바퀴 둘레값

// Speed Parameter
#define  MAX_SPEEDRPM 8000 //최대 속도RPM
#define  MAX_PWM 255  //PWM 값

// 변수 선언부
// Motor Speed, DIR
float back_wheel_speed, right_wheel_speed, left_wheel_speed;
float matrix_w_b[3][3];
float matrix_b_w[3][3];
int i, j;
bool backdir;
bool leftdir;
bool rightdir;

// 초음파 timer
unsigned long cur_time ;
unsigned long pre_time ;

const long utime = 2500; // timer loop time(us)
const long mtime = 100; // Ultrasensor timer loop time(ms)

//초음파 alpha filter
unsigned long  pre_distance_F;
unsigned long  pre_distance_L;
unsigned long  pre_distance_R;

unsigned long  pre_distance_side_L;
unsigned long  pre_distance_side_R;

const float alpha = 0.90;
const float beta = (1 - alpha);

int front_detection_distance1 = 50;
int front_detection_distance2 = 40;
int left_detection_distance = 30;
int right_detection_distance = 30;
int sideL_detection_distance = 30;
int sideR_detection_distance = 30;

//필터 적용된 distance
unsigned long  distance_F;
unsigned long  distance_L;
unsigned long  distance_R;

unsigned long  distance_side_L;
unsigned long  distance_side_R;

bool start_robot = false;
float motor_forward_speed = 0.0; // 전진 속도 -: (x)
float motor_turnR_speed = 0.0; // +: 우측(z)
float motor_turnL_speed = 0.0; // -:좌측 회전속도(z)
float motor_moveTosideL_speed = 0.0; // +: 좌측으로 이동(y)
float motor_moveTosideR_speed = 0.0; // -: 우측으로 이동(y)

float f_decay_rate = 0.7; //전방 장애물 감지 시 속도 감속률
float side_decay_rate = 0.7; // 좌,우 이동 후 반대로 이동 시 속도 감속률

int front_check = 0;

float forward_speed_max = 1.0;
float side_speed_max = 1.0;    
float turn_speed_max = 0.7;    

int front_delay = 100;
int uturn_delay = 2000; //ms
int turn_delay = 700;
int side_delay = 300;

int front_stay_time = 20; //전방 정지 감지시간

//// ros 선언 부////
ros::NodeHandle nh;

void Byu_Cb(const geometry_msgs::Twist& byu_val) // 명령 값 받아서 byu robot 제어
{
  motor_forward_speed = byu_val.linear.x;
  if (motor_forward_speed > forward_speed_max) motor_forward_speed = forward_speed_max;
  motor_forward_speed = -motor_forward_speed;

  motor_moveTosideR_speed = byu_val.linear.y;
  if (motor_moveTosideR_speed > side_speed_max) motor_moveTosideR_speed = side_speed_max;
  motor_moveTosideL_speed = -motor_moveTosideR_speed;

  motor_turnR_speed = byu_val.angular.z;
  if (motor_turnR_speed > turn_speed_max) motor_turnR_speed = turn_speed_max;
  motor_turnL_speed = -motor_turnR_speed;

  start_robot = true;
}

ros::Subscriber<geometry_msgs::Twist> sub("/byu_control", Byu_Cb); //제어값받음

//////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
/////////////  함수 정의부/////////////////////////////////////////

//////////////////////////////////////////////////////////////
void Collision_Avoidance() {

  if (IR_sensor_check == true)
  {
    drive_line_body_frame(0, 0, 0, 100);
    drive_line_body_frame(-motor_forward_speed, 0, 0, 2000); //후진
    drive_line_body_frame(0, 0, motor_turnR_speed, turn_delay * 6); // U턴
  }
  else
  {
    if (distance_F <= front_detection_distance1) { // 전방에 장애물이 감지되면
      drive_line_body_frame(motor_forward_speed * f_decay_rate , 0, 0, 0); //속도감소
      if (distance_F <= front_detection_distance2) {  // 정면이 막혔을 때
        drive_line_body_frame(0, 0, 0, front_delay); //정지
        front_check += 1;
        if (front_check >= front_stay_time) { // front_check +10 -> +1s
          drive_line_body_frame(0, 0, motor_turnR_speed, turn_delay * 6);
          front_check = 0;
        }
        Avoidance_Check();
      }
    }
    else { // 전방에 장애물 감지 안되었을 때,정면이 안 막혔을 때
      Avoidance_Check();
    }
  }
  drive_line_body_frame(motor_forward_speed, 0, 0, 0);  // 정상주행 앞으로
}

void Avoidance_Check() {

  if (distance_L <= left_detection_distance && distance_R <= right_detection_distance) { //좌우가 거리가 측정되고, 다 막히면 U턴
    drive_line_body_frame(0, 0, motor_turnR_speed, uturn_delay);
    front_check = 0;
  }
  else if (distance_L <= left_detection_distance) { //좌측 막히면 우측으로 회전
    drive_line_body_frame(0, 0, motor_turnR_speed, turn_delay);
    front_check = 0;
  }
  else if (distance_R <= right_detection_distance) { //우측 막히면 좌측으로 회전
    drive_line_body_frame(0, 0, motor_turnL_speed, turn_delay);
    front_check = 0;
  }
  if (distance_side_L <= sideL_detection_distance) { // 앞이 막혀서 회전 한 후에 좌측에 장애물이 가까이 있을 경우 우측으로 이동하여 거리를 두도록 한다.
    drive_line_body_frame( 0, motor_moveTosideR_speed , 0, side_delay);
    front_check = 0;
    if (distance_side_R <= sideR_detection_distance) { // 좌측으로 움직였는데 반대쪽 장애물에 가까워진 경우 반대로 다시 살짝 움직여준다.
      drive_line_body_frame( 0, motor_moveTosideL_speed * side_decay_rate, 0, side_delay);
    }
  }
  else if (distance_side_R <= sideR_detection_distance) { // 앞이 막혀서 회전 한 후에 우측에 장애물이 가까이 있을 경우 좌측으로 이동하여 거리를 두도록 한다.
    drive_line_body_frame( 0, motor_moveTosideL_speed , 0, side_delay);
    front_check = 0;
    if (distance_side_L <= sideL_detection_distance) { // 좌측으로 움직였는데 반대쪽 장애물에 가까워진 경우 반대로 다시 살짝 움직여준다.
      drive_line_body_frame( 0, motor_moveTosideR_speed * side_decay_rate, 0, side_delay);
    }
  }
}

////// 초음파센서 /////////

void SetupUltraPin() {
  pinMode(TRIG_Front, OUTPUT);
  pinMode(ECHO_Front, INPUT);

  pinMode(TRIG_Right, OUTPUT);
  pinMode(ECHO_Right, INPUT);

  pinMode(TRIG_Left, OUTPUT);
  pinMode(ECHO_Left, INPUT);

  pinMode(TRIG_side_decay_rateL, OUTPUT);
  pinMode(ECHO_side_decay_rateL, INPUT);

  pinMode(TRIG_side_decay_rateR, OUTPUT);
  pinMode(ECHO_side_decay_rateR, INPUT);
}

void Read_distance() {
  IR_sensor_check = digitalRead(IR_SENSOR);

  distance_F = UltraSonic(TRIG_Front, ECHO_Front);
  distance_F = round((alpha * distance_F) + ( beta * pre_distance_F));
  if (distance_F < DIST_MIN) distance_F = DIST_MAX * 2; // 최소 측정 거리 이하이면 물체가 측정거리 밖에 있다고 본다.
  pre_distance_F = distance_F;

  distance_L = UltraSonic(TRIG_Left, ECHO_Left);
  distance_L = round((alpha * distance_L ) + (beta * pre_distance_L));
  if (distance_L < DIST_MIN) distance_L = DIST_MAX * 2;
  pre_distance_L = distance_L;

  distance_R = UltraSonic(TRIG_Right, ECHO_Right);
  distance_R = round((alpha * distance_R ) + (beta * pre_distance_R));
  if (distance_R < DIST_MIN) distance_R = DIST_MAX * 2;
  pre_distance_R = distance_R;

  distance_side_L = UltraSonic(TRIG_side_decay_rateL, ECHO_side_decay_rateL);
  distance_side_L = round((alpha * distance_side_L) + (beta * pre_distance_side_L));
  if (distance_side_L < DIST_MIN) distance_side_L = DIST_MAX * 2;
  pre_distance_side_L = distance_side_L;

  distance_side_R = UltraSonic(TRIG_side_decay_rateR, ECHO_side_decay_rateR);
  distance_side_R = round((alpha * distance_side_R) + (beta * pre_distance_side_R));
  if (distance_side_R < DIST_MIN) distance_side_R = DIST_MAX * 2;
  pre_distance_side_R = distance_side_R;
}

unsigned long UltraSonic(char TRIG, char ECHO) {

  //trigger 발사
  unsigned long distance;

  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  //echo 핀 입력으로 부터 거리를 cm 단위로 계산
  distance = pulseIn(ECHO, HIGH, DIST_S) / 58.2; //최대 측정 사용시 pulseIn(ECHO,HIGH,DIST_S), pulseIn 반환: unsigned long

  if (distance < DIST_MIN) distance = DIST_MAX * 2;

  return distance;
}


//// Motor Pin Setup ///////////////
void SetupMotorPin() {
  pinMode(BACK_PWM, OUTPUT);
  pinMode(LEFT_PWM, OUTPUT);
  pinMode(RIGHT_PWM, OUTPUT);

  pinMode(BACK_DIR, OUTPUT);
  pinMode(LEFT_DIR, OUTPUT);
  pinMode(RIGHT_DIR, OUTPUT);

  pinMode(MOTOR_DRIVER_RELAY, OUTPUT);
  digitalWrite(MOTOR_DRIVER_RELAY, LOW);
}
//// Motor Speed 계산부
void generate_matrix_wheel_body(float matrix_w_b[][3], float matrix_b_w[][3]) {
  float angle_between_wheels[3];
  angle_between_wheels[0] = 180 * M_PI / 180; //rad
  angle_between_wheels[1] = (-60) * M_PI / 180; //rad
  angle_between_wheels[2] = 60 * M_PI / 180; //rad

  for (i = 0; i < 3; i++)
  {
    matrix_b_w[i][0] = -BODY_RADIUS;
    matrix_b_w[i][1] = sin(angle_between_wheels[i]);
    matrix_b_w[i][2] = -cos(angle_between_wheels[i]);
  }
  for (i = 0; i < 3; i++)
    for (j = 0; j < 3; j++)
      matrix_w_b[i][j] = matrix_b_w[i][j]; //create a copy
  Matrix.Invert((float*)matrix_w_b, NR_OMNIWHEELS); // this thing stores the inverted matrix in itself

}

bool SetDirection(float value) { //모터 방향
  return value > 0;
}

///////  바퀴속도 조정  //////////////
void Set_Speed(float desired_speed_body_frame[]) {

  back_wheel_speed = right_wheel_speed = left_wheel_speed = 0;

  for (int i = 0; i <= 2; i++)
  {
    back_wheel_speed = back_wheel_speed + matrix_b_w[0][i] * desired_speed_body_frame[i];
    left_wheel_speed = left_wheel_speed + matrix_b_w[2][i] * desired_speed_body_frame[i];
    right_wheel_speed = right_wheel_speed + matrix_b_w[1][i] * desired_speed_body_frame[i];
  }
  // 휠의 회전 방향
  backdir = SetDirection(back_wheel_speed);
  leftdir = SetDirection(left_wheel_speed);
  rightdir = SetDirection(right_wheel_speed);

  // 휠 속도 값
  back_wheel_speed = round(((abs(back_wheel_speed) * 6 * 10.0) / WHEEL_CIRC) * REDUCTION_RATIO_NAMIKI_MOTOR);
  left_wheel_speed = round(((abs(left_wheel_speed) * 6 * 10.0) / WHEEL_CIRC) * REDUCTION_RATIO_NAMIKI_MOTOR);
  right_wheel_speed = round(((abs(right_wheel_speed) * 6 * 10.0) / WHEEL_CIRC) * REDUCTION_RATIO_NAMIKI_MOTOR);

  // 최대 RPM과 비교하여 휠속도 제어
  if (back_wheel_speed >= MAX_SPEEDRPM) back_wheel_speed = MAX_SPEEDRPM;
  if (left_wheel_speed >= MAX_SPEEDRPM) left_wheel_speed = MAX_SPEEDRPM;
  if (right_wheel_speed >= MAX_SPEEDRPM) right_wheel_speed = MAX_SPEEDRPM;

  // map함수를 이용하여 0~MAX_SPEEDRPM을 0~MAX_PWM으로 변환
  back_wheel_speed = map(back_wheel_speed, 0, MAX_SPEEDRPM, 0, MAX_PWM);
  left_wheel_speed = map(left_wheel_speed, 0, MAX_SPEEDRPM, 0, MAX_PWM);
  right_wheel_speed = map(right_wheel_speed, 0, MAX_SPEEDRPM, 0, MAX_PWM);
}

///// Motor 구동 함수 ////////
void drive_line_body_frame(float velocity_x, float velocity_y, float velocity_z, float duration) { // duration: ms
  float desired_speed_body_frame[3] = {0};
  desired_speed_body_frame[0] = velocity_z; // rotations rad/sec
  desired_speed_body_frame[1] = velocity_x; // x directions, mm/sec
  desired_speed_body_frame[2] = velocity_y; // y direction, mm/sec

  Set_Speed(desired_speed_body_frame);

  BackrunPWM(back_wheel_speed, backdir);
  LeftrunPWM(left_wheel_speed, leftdir);
  RightrunPWM(right_wheel_speed, rightdir);

  if ( duration > 0) {
    delay(duration);
  }
}

void BackrunPWM(unsigned int PWM, bool dir) {
  digitalWrite(BACK_DIR, dir);
  analogWrite(BACK_PWM, PWM);
}
void LeftrunPWM(unsigned int PWM, bool dir) {
  digitalWrite(LEFT_DIR, dir);
  analogWrite(LEFT_PWM, PWM);
}
void RightrunPWM(unsigned int PWM, bool dir) {
  digitalWrite(RIGHT_DIR, dir);
  analogWrite(RIGHT_PWM, PWM);
}

////// Setup ////////////////
void setup() {

  SetupMotorPin();  // Motor Pin 설정
  SetupUltraPin();  // Ultra Pin 설정
  pinMode(IR_SENSOR, INPUT);

  nh.initNode();
  nh.subscribe(sub);

  delay(2000);

  digitalWrite(MOTOR_DRIVER_RELAY, HIGH); // 모터 드라이버 릴레이 스위치

  generate_matrix_wheel_body(matrix_w_b, matrix_b_w);

  drive_line_body_frame(0, 0, 0, 0);
}

//unsigned long s_time = 0; // 루프 타임체크용
//unsigned long e_time = 0; // 루프 타임체크용

//////////////////////////////////////////////////////
////////  Loop //////////////////////////////

void loop() {

  nh.spinOnce();

  if ( start_robot == true)
  {
    cur_time = millis();

    if (cur_time - pre_time >= mtime)
    {
      Read_distance(); // 초음파 센서 값 읽는 부분
      Collision_Avoidance(); // 충돌회피 알고리즘으로 모바일 로봇 구동   
      
      pre_time = cur_time ;
    }
  }

}
