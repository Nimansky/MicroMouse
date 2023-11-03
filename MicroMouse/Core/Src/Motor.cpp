/*
 * Motor.cpp
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#include <Motor.h>

Motor::Motor(TIM_HandleTypeDef* PWMTimer, uint32_t forwardChannel, uint32_t reverseChannel, PIDController* pidController) {
	tim = PWMTimer;
	fwdChan = forwardChannel;
	revChan = reverseChannel;
	pid = pidController;
}

void Motor::recalcPIDSpeed(){

	float pidSpeed = pid->calculateSignal();
	int sign = (pidSpeed > 0) - (pidSpeed < 0); //1 for pos, -1 for neg, 0 for 0
	pidSpeed = fabs(pidSpeed) > 1.0 ? 1.0 : fabs(pidSpeed);

	setSpeed(pidSpeed * sign * dir);
	pid->setEncoderDirection(sign);
}

/*
 * numFields: number of maze fields to proceed
 * direction: 1 for forwards, -1 for backwards
 */
void Motor::drive(uint32_t counts, int8_t direction){

	if(driving) return;

	pid->setSetPosition(counts); //setposition is amount of counts to turn the wheel to
	pid->resetEncoderDistance(); //reset traveled distance to 0

	dir = direction;

	recalcPIDSpeed();

	start();
}

bool Motor::isDriving(){
	return driving;
}

/**
 * sets the speed of the motor to anything between -1 and 1 * maxSpeed
 * note: 0 is not a valid argument to pass, since to stop the motor, the method Motor::stop() should be called
 */
void Motor::setSpeed(float speed){
	float absSpeed = fabs(speed);
	if(speed >= -1.0 && speed < 0){ //case reverse
		switch(revChan){
		case TIM_CHANNEL_1:
			tim->Instance->CCR1 = (65535 * absSpeed)-1;
			break;
		case TIM_CHANNEL_2:
			tim->Instance->CCR2 = (65535 * absSpeed)-1;
			break;
		case TIM_CHANNEL_3:
			tim->Instance->CCR3 = (65535 * absSpeed)-1;
			break;
		case TIM_CHANNEL_4:
			tim->Instance->CCR4 = (65535 * absSpeed)-1;
			break;
		}
		switch(fwdChan){
		case TIM_CHANNEL_1:
			tim->Instance->CCR1 = 65535;
			break;
		case TIM_CHANNEL_2:
			tim->Instance->CCR2 = 65535;
			break;
		case TIM_CHANNEL_3:
			tim->Instance->CCR3 = 65535;
			break;
		case TIM_CHANNEL_4:
			tim->Instance->CCR4 = 65535;
			break;
		}
	}

	if(speed > 0 && speed <= 1.0){ //case forward
		switch(revChan){
		case TIM_CHANNEL_1:
			tim->Instance->CCR1 = 65535;
			break;
		case TIM_CHANNEL_2:
			tim->Instance->CCR2 = 65535;
			break;
		case TIM_CHANNEL_3:
			tim->Instance->CCR3 = 65535;
			break;
		case TIM_CHANNEL_4:
			tim->Instance->CCR4 = 65535;
			break;
		}
		switch(fwdChan){
		case TIM_CHANNEL_1:
			tim->Instance->CCR1 = (65535 * absSpeed)-1;
			break;
		case TIM_CHANNEL_2:
			tim->Instance->CCR2 = (65535 * absSpeed)-1;
			break;
		case TIM_CHANNEL_3:
			tim->Instance->CCR3 = (65535 * absSpeed)-1;
			break;
		case TIM_CHANNEL_4:
			tim->Instance->CCR4 = (65535 * absSpeed)-1;
			break;
		}
	}
}


void Motor::start(){
	driving = true;
	HAL_TIM_PWM_Start(tim, fwdChan);
	HAL_TIM_PWM_Start(tim, revChan);
}


void Motor::stop(){
	driving = false;
	HAL_TIM_PWM_Stop(tim, fwdChan);
	HAL_TIM_PWM_Stop(tim, revChan);
}


Motor::~Motor() {
	// TODO Auto-generated destructor stub
}

