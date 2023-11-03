/*
 * Executer.h
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#ifndef INC_EXECUTER_H_
#define INC_EXECUTER_H_

#include "Defines.h"
#include "usart.h"
#include "CommandMessage.h"
#include "DataMessage.h"
#include "RotaryEncoder.h"
#include <cstring>
#include "AnalogSensor.h"
#include "Motor.h"
#include "PIDController.h"

extern struct SensorData {
	uint32_t rpmL = 0;
	uint32_t rpmR = 0;
	uint32_t collFrontRight = 0;
	uint32_t collFrontLeft = 0;
	uint32_t collRight = 0;
	uint32_t collLeft = 0;
	uint32_t distance = 0;
} sensorData;


extern void collectSensorData();
extern uint32_t getSensorData(Sensor sensor);
extern void sendDataMessage(DataMessage msg);
extern void sendMessage(Message msg);
extern void executeCommand(CommandMessage cmd);


#endif /* INC_EXECUTER_H_ */
