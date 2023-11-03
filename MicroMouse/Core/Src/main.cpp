/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "Motor.h"
#include "main.h"
#include "i2c.h"
#include "dma.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"
#include "Defines.h"
#include "CommandMessage.h"
#include "DataMessage.h"
#include "Executer.h"
#include "Motor.h"
#include "RotaryEncoder.h"
#include "AnalogSensor.h"
#include "vl53l1_api.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

RotaryEncoder encLeft = RotaryEncoder(ENCLA_PIN, ENCLB_PIN, ENCLA_PORT, ENCLB_PORT);
RotaryEncoder encRight = RotaryEncoder(ENCRA_PIN, ENCRB_PIN, ENCRA_PORT, ENCRB_PORT);

// PIDController(encoder, kp, kd, ki)
PIDController pidLeft = PIDController(&encLeft, 0.2, 0.0, 0.0);
PIDController pidRight = PIDController(&encRight, 0.2, 0.0, 0.0);

Motor motorLeft = Motor(&htim3, TIM_CHANNEL_4, TIM_CHANNEL_3, &pidLeft);
Motor motorRight = Motor(&htim15, TIM_CHANNEL_2, TIM_CHANNEL_1, &pidRight);

AnalogSensor distanceSensor = AnalogSensor();

uint8_t Rx_buf[12]; //messages are 48 bit

bool stoppedMotorL = false;
bool stoppedMotorR = false;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM15_Init();
  MX_DMA_Init();
  MX_I2C1_Init();
  MX_USART5_UART_Init();
  MX_TIM1_Init();
  MX_TIM3_Init();
  MX_TIM6_Init();
  /* USER CODE BEGIN 2 */

  HAL_TIM_Base_Start_IT(&htim1);
  HAL_TIM_Base_Start_IT(&htim6);

  distanceSensor.init();

  HAL_UART_Receive_DMA(&huart5, Rx_buf, 6);

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL6;
  RCC_OscInitStruct.PLL.PREDIV = RCC_PREDIV_DIV1;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_I2C1;
  PeriphClkInit.I2c1ClockSelection = RCC_I2C1CLKSOURCE_HSI;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin){

	//each rising and falling edge on the A  or B signal, update the encoder values
	if(GPIO_Pin == ENCRA_PIN || GPIO_Pin == ENCRB_PIN){
		encRight.update_encoder(GPIO_Pin);
	}
	else if(GPIO_Pin == ENCLA_PIN || GPIO_Pin == ENCLB_PIN){
		encLeft.update_encoder(GPIO_Pin);
	}

}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef* htim){
	if(htim == &htim1){
		//TIM1 interrupts at 10Hz (every 100 ms)
		encLeft.update_speed();
		encRight.update_speed();
		distanceSensor.update_sensor();


		collectSensorData();
	}

	if(htim == &htim6){
		//TIM6 interrupts at 1kHz (every 1 ms)
		if(motorLeft.isDriving()){

			motorLeft.recalcPIDSpeed();

			if(pidLeft.reachedSetPosition()){
				motorLeft.stop();
				stoppedMotorL = true;
			}

		}

		if(motorRight.isDriving()){

			motorRight.recalcPIDSpeed();

			if(pidRight.reachedSetPosition()){
				motorRight.stop();
				stoppedMotorR = true;
			}

		}

		if (stoppedMotorL && stoppedMotorR) {
			sendMessage(Message(MOVEMENT_DONE));
			stoppedMotorL = false;
			stoppedMotorR = false;
		}
	}

}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart){
	HAL_UART_Receive_DMA(huart, Rx_buf, 6);
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
	if(huart == &huart5){
		//only if initiation sequence is correct
		if(Rx_buf[0] == 0x1A && (Rx_buf[1]>>4) == 0x4){
			uint8_t cmd = Rx_buf[1] & 0x0F; //cmd is just the lower 4 bits of the second byte
			uint32_t param = (Rx_buf[2] << 24) | (Rx_buf[3] << 16) | (Rx_buf[4] << 8) | (Rx_buf[5]);
			CommandMessage cmdMsg((Command)cmd, param);
			executeCommand(cmdMsg);
		}
	}
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
