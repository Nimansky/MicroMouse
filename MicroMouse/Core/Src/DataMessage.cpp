/*
 * DataMessage.cpp
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#include "DataMessage.h"

DataMessage::DataMessage(Sensor s, uint32_t sensorData) : Message(SENSOR_DATA) {
	sensor = s;
	data = sensorData;
}

Sensor DataMessage::getSensor(){
	return sensor;
}

uint32_t DataMessage::getData(){
	return data;
}

DataMessage::~DataMessage() {
	// TODO Auto-generated destructor stub
}

