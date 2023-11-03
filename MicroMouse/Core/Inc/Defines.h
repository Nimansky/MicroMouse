/*
 * Defines.h
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#ifndef INC_DEFINES_H_
#define INC_DEFINES_H_

#define FREQUENCY 48000000 //clock runs at 48 MHz
#define TIMER1_TIMEOUT_MS 100 //milliseconds until tim1 is supposed to issue an interrupt
#define TIMER6_TIMEOUT_MS 1

#define PID_TOLERANCE 100 // error tolerance for the motors/pid in counts

#define FIELD_LENGTH 20.3f // length and width of ONE block in the maze in centimeters
#define WHEEL_CIRCUMFERENCE 25.76f // circumference of the MicroMouse's wheel in centimeters, given by 2*pi*r with r = 4.1cm
#define TURN_RADIUS 3.8f //turn radius of the robot as measured by ourselves

#define RESOLUTION 12 //as per datasheet the resolution is 12 CPR when counting both edges of the A and the B signal (4 edges)
#define GEAR_RATIO 100.37f //gear ratio of the motors as per datasheet

#define ENCLA_PIN GPIO_PIN_15
#define ENCLA_PORT GPIOC

#define ENCLB_PIN GPIO_PIN_2
#define ENCLB_PORT GPIOA

#define ENCRA_PIN GPIO_PIN_1
#define ENCRA_PORT GPIOA

#define ENCRB_PIN GPIO_PIN_0
#define ENCRB_PORT GPIOA

#define COLLISION_FRONT_LEFT_PIN GPIO_PIN_0
#define COLLISION_FRONT_LEFT_PORT GPIOF

#define COLLISION_FRONT_RIGHT_PIN GPIO_PIN_14
#define COLLISION_FRONT_RIGHT_PORT GPIOC

#define COLLISION_SIDE_LEFT_PIN GPIO_PIN_13
#define COLLISION_SIDE_LEFT_PORT GPIOC

#define COLLISION_SIDE_RIGHT_PIN GPIO_PIN_7
#define COLLISION_SIDE_RIGHT_PORT GPIOB


typedef enum{
	SENSOR_DATA,
	COMMAND,
	MOVEMENT_DONE
} MessageType;

typedef enum{
	RPM_LEFT,	//rotary encoder left speed
	RPM_RIGHT,  //rotary encoder right speed
	COLLISION_FRONT_RIGHT, //digital sensor front right
	COLLISION_FRONT_LEFT, //digital sensor front left
	COLLISION_RIGHT,  //digital sensor right side
	COLLISION_LEFT, //digital sensor left side
	DISTANCE_FRONT, //analog i2c distance sensor front
} Sensor;

typedef enum{
	SEND_SENSOR_DATA, //MicroMouse should send specific sensor data (sensor as param)
	TURN_LEFT, //amount of 90-degree-steps as param
	TURN_RIGHT, //amount of 90-degree-steps as param
	MOVE_FORWARD, //amount of fields as param
	MOVE_BACKWARD //amount of fields as param
} Command;


#endif /* INC_DEFINES_H_ */
