/*
 * CommandMessage.cpp
 *
 *  Created on: Sep 12, 2023
 *      Author: niman
 */

#include "CommandMessage.h"

CommandMessage::CommandMessage(Command cmd, uint32_t parameter) : Message(COMMAND) {
	param = parameter;
	command = cmd;
}

Command CommandMessage::getCommand(){
	return command;
}

uint32_t CommandMessage::getParam(){
	return param;
}

CommandMessage::~CommandMessage() {
	// TODO Auto-generated destructor stub
}

