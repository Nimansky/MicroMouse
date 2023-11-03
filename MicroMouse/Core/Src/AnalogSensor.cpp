/*
 * AnalogSensor.cpp
 *
 *  Created on: Sep 13, 2023
 *      Author: niman
 */

#include "AnalogSensor.h"

AnalogSensor::AnalogSensor() {

}

void AnalogSensor::init(){
	ptr = -1;
	Dev->I2cHandle = &hi2c1;
	Dev->I2cDevAddr = 0x52u;
	auto status = VL53L1_WaitDeviceBooted(Dev);
	VL53L1_DataInit(Dev);
	VL53L1_StaticInit(Dev);
	VL53L1_SetDistanceMode(Dev, VL53L1_DISTANCEMODE_SHORT);
	VL53L1_SetMeasurementTimingBudgetMicroSeconds(Dev, 50000);
	VL53L1_SetInterMeasurementPeriodMilliSeconds(Dev, 500);
	VL53L1_StartMeasurement(Dev);
}

void AnalogSensor::update_sensor(){
	uint8_t rdy = 0;
	VL53L1_GetMeasurementDataReady(Dev, &rdy);
	if(rdy){
		ptr = (ptr+1) % 5;  //circular buffer
		VL53L1_RangingMeasurementData_t rd;
		VL53L1_GetRangingMeasurementData(Dev, &rd);
		RangingData[ptr] = rd;
		VL53L1_ClearInterruptAndStartMeasurement(Dev);
	}
}

uint32_t AnalogSensor::getLatestMeasurement(){
	if(ptr > -1){
		uint16_t latestData = RangingData[ptr].RangeMilliMeter;
		return latestData;
	}else{
		return 0;
	}
}

AnalogSensor::~AnalogSensor() {
	// TODO Auto-generated destructor stub
}

