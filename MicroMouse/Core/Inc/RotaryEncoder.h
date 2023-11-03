/*
 * RotaryEncoder.h
 *
 *  Created on: Sep 9, 2023
 *      Author: niman
 */

#ifndef SRC_ROTARYENCODER_H_
#define SRC_ROTARYENCODER_H_

#include "stm32f0xx_hal.h"
#include "Defines.h"

class RotaryEncoder{
public:
	RotaryEncoder(uint16_t encoderPinA, uint16_t encoderPinB, GPIO_TypeDef* encoderPortA, GPIO_TypeDef* encoderPortB);
	void update_encoder(uint16_t pin);
	void update_speed();
	void reset_encoder();
	void setDirection(int8_t dir);
	virtual ~RotaryEncoder();
	float getSpeed();
	int32_t getPosition();
	void resetPosition();

private:
	uint32_t triggerCount = 0;
	int8_t direction = 0;
	uint16_t encPinA;
	uint16_t encPinB;
	int32_t position = 0;
	GPIO_TypeDef* encPortA;
	GPIO_TypeDef* encPortB;

	float speed = 0;
};

extern RotaryEncoder encLeft;
extern RotaryEncoder encRight;

#endif /* SRC_ROTARYENCODER_H_ */
