/*
 * Motor.h
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#ifndef SRC_MOTOR_H_
#define SRC_MOTOR_H_

#include <cmath>
#include "stm32f0xx_hal.h"
#include "Defines.h"
#include "PIDController.h"

class Motor {
public:
	Motor(TIM_HandleTypeDef* PWMTimer, uint32_t forwardChannel, uint32_t reverseChan, PIDController* pidController);
	void setSpeed(float speed);
	void recalcPIDSpeed();
	void drive(uint32_t counts, int8_t direction);
	void start();
	void stop();
	bool isDriving();

	virtual ~Motor();
private:
	float speed;
	int dir = 0;
	bool driving = false;
	TIM_HandleTypeDef* tim;
	PIDController* pid;
	uint32_t fwdChan;
	uint32_t revChan;

};

extern Motor motorLeft;
extern Motor motorRight;

#endif /* SRC_MOTOR_H_ */
