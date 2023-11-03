/*
 * AnalogSensor.h
 *
 *  Created on: Sep 13, 2023
 *      Author: niman
 */

#ifndef SRC_ANALOGSENSOR_H_
#define SRC_ANALOGSENSOR_H_

#include "vl53l1_api.h"
#include "i2c.h"

class AnalogSensor {
public:
	AnalogSensor();
	void init();
	void update_sensor();
	uint32_t getLatestMeasurement();
	virtual ~AnalogSensor();
private:
	int8_t ptr;
	VL53L1_RangingMeasurementData_t RangingData[5];
	VL53L1_Dev_t vl53l1_c;
	VL53L1_DEV Dev = &vl53l1_c;
};

extern AnalogSensor distanceSensor;

#endif /* SRC_ANALOGSENSOR_H_ */
