/*
 * RotaryEncoder.cpp
 *
 *  Created on: Sep 9, 2023
 *      Author: niman
 */

#include "RotaryEncoder.h"

RotaryEncoder::RotaryEncoder(uint16_t encoderPinA, uint16_t encoderPinB, GPIO_TypeDef* encoderPortA, GPIO_TypeDef* encoderPortB) {
	encPinA = encoderPinA;
	encPinB = encoderPinB;
	encPortA = encoderPortA;
	encPortB = encoderPortB;
}

RotaryEncoder::~RotaryEncoder() {
	// TODO Auto-generated destructor stub
}

void RotaryEncoder::update_encoder(uint16_t pin){
	//if the values of A and B are different at rising/falling edge, the movement is forward, if it's the same, it's backwards
	//int direction;
	//if(pin == encPinA){
	//direction = HAL_GPIO_ReadPin(encPortB, encPinB) != HAL_GPIO_ReadPin(encPortA, encPinA) ? 1 : -1;
	//}else if(pin == encPinB){
	//	direction = HAL_GPIO_ReadPin(encPortB, encPinB) == HAL_GPIO_ReadPin(encPortA, encPinA) ? 1 : -1;
	//}

	triggerCount++;

	position += direction;
}

void RotaryEncoder::setDirection(int8_t dir){
	direction = dir;
}

void RotaryEncoder::resetPosition(){
	position = 0;
	direction = 0;
}

int32_t RotaryEncoder::getPosition(){
	return position;
}

void RotaryEncoder::reset_encoder(){
	triggerCount = 0;
	direction = 0;
}

float RotaryEncoder::getSpeed(){
	return speed;
}

void RotaryEncoder::update_speed(){

	__disable_irq();
	uint32_t tmp = triggerCount;
	triggerCount = 0;
	__enable_irq();

	float rpms = ((float)(tmp)/(RESOLUTION*GEAR_RATIO)); //rotations per 100 ms
	float rpm = rpms * 600; //rotations per minute
	speed = rpm;
}
