/*
 * PIDController.cpp
 *
 *  Created on: Sep 23, 2023
 *      Author: niman
 */

#include "PIDController.h"




void PIDController::setSetPosition(uint32_t setpos) {
	setPosition = setpos;
	errorIntegral = 0;
	currTime = 0;
	prevError = 0;
	prevTime = 0;
}

bool PIDController::reachedSetPosition(){
	return fabs(setPosition - enc->getPosition()) <= PID_TOLERANCE;
}

void PIDController::resetEncoderDistance(){
	enc->resetPosition();
}

void PIDController::setEncoderDirection(int8_t dir){
	enc->setDirection(dir);
}

uint32_t PIDController::getSetPosition(){
	return setPosition;
}

float PIDController::calculateSignal() {
	error = (int32_t)setPosition - enc->getPosition();
	currTime += TIMER6_TIMEOUT_MS;

	errorDifferential = float(error - prevError)/(currTime - prevTime);
	errorIntegral += float(error) * (currTime - prevTime);

	prevTime = currTime;
	prevError = error;

	return (kp*error + kd*errorDifferential + ki*errorIntegral) / 65535;
}

PIDController::~PIDController() {
	// TODO Auto-generated destructor stub
}

