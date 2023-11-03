/*
 * DataMessage.h
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#ifndef SRC_DATAMESSAGE_H_
#define SRC_DATAMESSAGE_H_

#include "Defines.h"
#include "Message.h"
#include "main.h"

class DataMessage : Message {
public:
	DataMessage(Sensor s, uint32_t sensorData);
	Sensor getSensor();
	uint32_t getData();
	virtual ~DataMessage();
private:
	Sensor sensor;
	uint32_t data;
};

#endif /* SRC_DATAMESSAGE_H_ */
