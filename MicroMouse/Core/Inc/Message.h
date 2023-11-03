/*
 * Message.h
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#ifndef SRC_MESSAGE_H_
#define SRC_MESSAGE_H_

#include "Defines.h"

class Message {
public:
	Message(MessageType msgType);
	MessageType getMessageType();
	virtual ~Message();
private:
	MessageType messageType;
};

#endif /* SRC_MESSAGE_H_ */
