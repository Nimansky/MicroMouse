/*
 * CommandMessage.h
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#ifndef SRC_COMMANDMESSAGE_H_
#define SRC_COMMANDMESSAGE_H_

#include "Defines.h"
#include "Message.h"
#include "main.h"

class CommandMessage : Message {
public:
	CommandMessage(Command cmd, uint32_t parameter);
	Command getCommand();
	uint32_t getParam();
	virtual ~CommandMessage();
private:
	Command command;
	uint32_t param;
};

#endif /* SRC_COMMANDMESSAGE_H_ */
