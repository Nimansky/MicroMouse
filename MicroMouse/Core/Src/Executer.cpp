/*
 * Executer.c
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#include "Executer.h"

struct SensorData sensorData;

void collectSensorData(){

	float f = encLeft.getSpeed();
	uint32_t ret = 0;
	memcpy(&ret, &f, sizeof(float));
	sensorData.rpmL = ret;

	f = encRight.getSpeed();
	ret = 0;
	memcpy(&ret, &f, sizeof(float));
	sensorData.rpmR = ret;

	sensorData.collFrontRight = HAL_GPIO_ReadPin(COLLISION_FRONT_RIGHT_PORT, COLLISION_FRONT_RIGHT_PIN);
	sensorData.collFrontLeft = HAL_GPIO_ReadPin(COLLISION_FRONT_LEFT_PORT, COLLISION_FRONT_LEFT_PIN);
	sensorData.collRight = HAL_GPIO_ReadPin(COLLISION_SIDE_RIGHT_PORT, COLLISION_SIDE_RIGHT_PIN);
	sensorData.collLeft = HAL_GPIO_ReadPin(COLLISION_SIDE_LEFT_PORT, COLLISION_SIDE_LEFT_PIN);
	sensorData.distance = distanceSensor.getLatestMeasurement();

}

uint32_t getSensorData(Sensor s){
	switch(s){
	case RPM_LEFT:
		return sensorData.rpmL;
	case RPM_RIGHT:
		return sensorData.rpmR;
	case COLLISION_FRONT_RIGHT:
		return sensorData.collFrontRight;
	case COLLISION_FRONT_LEFT:
		return sensorData.collFrontLeft;
	case COLLISION_RIGHT:
		return sensorData.collRight;
	case COLLISION_LEFT:
		return sensorData.collLeft;
	case DISTANCE_FRONT:
		return sensorData.distance;
	default:
		return 0;
	}
}


uint8_t Tx_buf_sens[12];

void sendDataMessage(DataMessage msg){

	Tx_buf_sens[0] = 0x1A;
	Tx_buf_sens[1] = 0x4 << 4 | msg.getSensor();

	uint32_t data = msg.getData();
	uint8_t *vp = (uint8_t *)&data;
	Tx_buf_sens[2] = vp[0];
	Tx_buf_sens[3] = vp[1];
	Tx_buf_sens[4] = vp[2];
	Tx_buf_sens[5] = vp[3];

	HAL_UART_Transmit_IT(&huart5, Tx_buf_sens, 6);
}

uint8_t Tx_buf_msg[12];

void sendMessage(Message msg){

	Tx_buf_msg[0] = 0x1A;
	Tx_buf_msg[1] = 0x4F;

	HAL_UART_Transmit_IT(&huart5, Tx_buf_msg, 6);
}


void executeCommand(CommandMessage cmd){
	Command cmdType = cmd.getCommand();

	switch(cmdType){
	case SEND_SENSOR_DATA: {  //sensor as Param
		Sensor sensor = (Sensor)cmd.getParam();
		uint32_t data = getSensorData(sensor);
		sendDataMessage(DataMessage(sensor, data));
		break;
	}
	case TURN_LEFT: { //amount of 90-degree-steps as param
		auto turns = cmd.getParam();

		//Turning left: left motor backwards, right motor forward
		motorLeft.drive(float(WHEEL_CIRCUMFERENCE/4)*turns*(GEAR_RATIO*RESOLUTION)/(WHEEL_CIRCUMFERENCE), -1);
		motorRight.drive(float(WHEEL_CIRCUMFERENCE/4)*turns*(GEAR_RATIO*RESOLUTION)/(WHEEL_CIRCUMFERENCE), 1);
		break;
	}
	case TURN_RIGHT: { //amount of 90-degree-steps as param
		auto turns = cmd.getParam();

		//Turning left: left motor forward, right motor backwards
		motorLeft.drive(float(WHEEL_CIRCUMFERENCE/4)*turns*(GEAR_RATIO*RESOLUTION)/(WHEEL_CIRCUMFERENCE), 1);
		motorRight.drive(float(WHEEL_CIRCUMFERENCE/4)*turns*(GEAR_RATIO*RESOLUTION)/(WHEEL_CIRCUMFERENCE), -1);
		break;
	}
	case MOVE_FORWARD: {//amount of fields as param
		auto steps = cmd.getParam();

		motorLeft.drive(float(FIELD_LENGTH)*steps*(GEAR_RATIO*RESOLUTION)/(WHEEL_CIRCUMFERENCE), 1);
		motorRight.drive(float(FIELD_LENGTH)*steps*(GEAR_RATIO*RESOLUTION)/(WHEEL_CIRCUMFERENCE), 1);
		break;
	}
	case MOVE_BACKWARD: {//amount of fields as param
		auto steps = cmd.getParam();

		motorLeft.drive(float(FIELD_LENGTH)*steps*(GEAR_RATIO*RESOLUTION)/(WHEEL_CIRCUMFERENCE), -1);
		motorRight.drive(float(FIELD_LENGTH)*steps*(GEAR_RATIO*RESOLUTION)/(WHEEL_CIRCUMFERENCE), -1);
		break;
	}
	}
}
