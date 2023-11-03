/*
 * PIDController.h
 *
 *  Created on: Sep 23, 2023
 *      Author: niman
 */

#ifndef SRC_PIDCONTROLLER_H_
#define SRC_PIDCONTROLLER_H_

#include "Defines.h"
#include "RotaryEncoder.h"
#include <cmath>

class PIDController {
public:
	PIDController(RotaryEncoder* encoder, float kp, float kd, float ki) : enc(encoder){
		this->kp = kp;
		this->kd = kd;
		this->ki = ki;
	};
	void setSetPosition(uint32_t setpos);
	bool reachedSetPosition();
	uint32_t getSetPosition();
	void resetEncoderDistance();
	float calculateSignal();
	void setEncoderDirection(int8_t dir);
	virtual ~PIDController();
private:
	float kp;
	float kd;
	float ki;
	RotaryEncoder* enc;
	float errorIntegral = 0;
	float  errorDifferential = 0;
	int32_t error = 0;
	int32_t prevError = 0;
	uint32_t setPosition = 0;
	uint32_t currTime = 0;
	uint32_t prevTime = 0;
};

extern PIDController pidLeft;
extern PIDController pidRight;

#endif /* SRC_PIDCONTROLLER_H_ */
