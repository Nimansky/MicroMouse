# MicroMouse - Readme

A [MicroMouse](https://en.wikipedia.org/wiki/Micromouse) built for a university school project by Nima Baradaran Hassanzadeh, Xian Chen and Christian Förster. The mouse is based on a Raspberry Pi 3B paired with an extension board hosting a STM32F030CC. As such, this project heavily involves sensor communication via I2C, inter-processor communication via UART, as well as a lot of STM32-internal timer and PWM logic. For exact specifics, please feel free to read the documentation.pdf!


# Pinouts

| MCU Pin | Mode           | GPIO Pin | Description            |
|---------|----------------|----------|------------------------|
| PF0     | Input          | GPIO6    | Sensor links vorn      |
| PC14    | Input          | GPIO7    | Sensor rechts vorn     |
| PC13    | Input          | GPIO4    | Sensor links Seite     |
| PB7     | Input          | GPIO5    | Sensor rechts Seite    |
| PB14    | TIM15 CH1      | GPIO0    | PWM Motor rechts (IN1) |
| PB15    | TIM15 CH2      | GPIO1    | PWM Motor rechts (IN2) |
| PB0     | TIM3 CH3       | LED1     | PWM Motor links (IN1)  |
| PB1     | TIM3 CH4       | LED2     | PWM Motor links (IN2)  |
| PA1     | EXTI Interrupt | GPIO13   | Motor Encoder rechts A |
| PC15    | EXTI Interrupt | GPIO14   | Motor Encoder links A  |
| PA0     | EXTI Interrupt | GPIO11   | Motor Encoder rechts B |
| PA2     | EXTI Interrupt | GPIO12   | Motor Encoder links B  |
| PB8     | I2C            | SCL      | Analog Sensor i2c SCL  |
| PB9     | I2C            | SDA      | Analog Sensor i2c SDA  |


# Communcation protocol

In order for the STM32 to be able to abstract away movement and the sensors from the actual solving algorithm, we had to come up with our own communication protocol.

## from master to mouse
    0x1A4 : Initiation sequence
    half byte : command type (current commands range from 0000-0100)
    32 bit param (padding if none needed)

## from mouse to master
    0x1A4 : Initiation sequence
    half byte : sensor (current sensors range from 0000-0110)
    32 bit sensor data