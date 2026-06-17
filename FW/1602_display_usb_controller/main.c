#include "CH552.H"
#include "CH552_RCC.h"
#include "CH552_TIMER.h"
#include "CH552_GPIO.h"
#include "CH552_PWM.h"
#include "CH552_USB_CDC.h"
#include "CH552_ST7066.h"

//Pins:
// LCD_E = P14
// LCD_DATA = P15
// G_PWM = P16
// LCD_CLK = P17
// R_PWM = P30
// LCD_CONTRAST = P31
// LCD_RS = P32
// B_PWM = P33
// UDP = P36
// UDM = P37

//PWM1 -> R_PWM
//PWM2 -> CONTRAST

int main()
{
	UINT8 prev_reset_typ;
	UINT16 com_wdog_count = 0;
	UINT16 com_wdog_limit = 0;
	
	UINT8 prev_control_line_state;
	UINT8 datagram[2];
	UINT16 bytes_available;
	UINT8 temp;
	UINT8 pwm_count = 0x08;
	
	UINT8 cursor_col = 0;
	UINT8 cursor_row = 0;
	UINT8 contrast = 45;
	UINT8 brightness_r = 127;
	UINT8 brightness_g = 127;
	UINT8 brightness_b = 127;
	UINT8 power_state = ST7066_DISP_ON_OFF_DISP_ON;
	
	rcc_set_clk_freq(RCC_CLK_FREQ_24M);
	
	gpio_set_mode(GPIO_MODE_PP, GPIO_PORT_1, GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 |GPIO_PIN_7);	//LCD_E, LCD_DATA, G_PWM, LCD_CLK
	gpio_set_mode(GPIO_MODE_PP, GPIO_PORT_3, GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3);	//R_PWM, LCD_CONTRAST, LCD_RS, B_PWM
	gpio_clear_pin(GPIO_PORT_1, GPIO_PIN_4);
	gpio_clear_pin(GPIO_PORT_3, GPIO_PIN_2);
	
	pwm_init(PWM_1 | PWM_2, PWM_ACTIVE_HIGH, 1, PWM_1_P30 | PWM_2_P31);
	pwm_set_duty_cycle(PWM_1, brightness_r);
	pwm_set_duty_cycle(PWM_2, contrast);
	timer_init(TIMER_0, NULL);
	timer_set_period(TIMER_0, FREQ_SYS / 1000ul);	//period is 1ms
	EA = 1;	//enable interupts
	E_DIS = 0;
	
	prev_reset_typ = RESET_KEEP;
	RESET_KEEP = rcc_get_rst_typ();
	if((RESET_KEEP == RCC_RST_TYP_WDOG) || (RESET_KEEP == RCC_RST_TYP_SOFT))
	{
		rcc_delay_ms(500);
	}
	
	st7066_init();
	
	cdc_init();
	cdc_set_serial_state(CDC_SS_TXCARRIER | CDC_SS_RXCARRIER);
	prev_control_line_state = cdc_control_line_state;
	while(!cdc_config);
	
	timer_start(TIMER_0);
	
	rcc_reload_wdog(0x00);
	rcc_set_wdog_rst_en(RCC_WDOG_ENABLED);
	
	while(TRUE)
	{
		bytes_available = cdc_bytes_available();
		temp = cdc_peek();
		if((bytes_available >= 2) && (temp & 0x80))	//Handle write datagram
		{
			cdc_read_bytes(datagram, 2);
			
			switch(datagram[0] & 0x7F)
			{
				case 0x0A:
					cursor_col = datagram[1];
					st7066_set_cursor(cursor_row, cursor_col);
					break;
				case 0x0B:
					cursor_row = datagram[1];
					st7066_set_cursor(cursor_row, cursor_col);
					break;
				
				case 0x0C:
					contrast = datagram[1];
					pwm_set_duty_cycle(PWM_2, contrast);
					break;
				case 0x0D:
					brightness_r = datagram[1];
					pwm_set_duty_cycle(PWM_1, brightness_r);
					break;
				case 0x0E:
					brightness_g = datagram[1];
					break;
				case 0x0F:
					brightness_b = datagram[1];
					break;
				
				case 0x10:
					st7066_init();
					cursor_col = 0;
					cursor_row = 0;
					break;
				case 0x11:
					st7066_clear_display();
					cursor_col = 0;
					cursor_row = 0;
					break;
				case 0x12:
					cursor_col = 0;
					cursor_row = datagram[1];
					st7066_clear_line(cursor_row);
					break;
				case 0x13:
					st7066_write_char(datagram[1]);
					cursor_col += 1;
					break;
				
				case 0x14:
					power_state = datagram[1] & (ST7066_DISP_ON_OFF_DISP_ON | ST7066_DISP_ON_OFF_CURS_ON | ST7066_DISP_ON_OFF_BLINK_ON);
					st7066_send_command(ST7066_COM_DISP_ON_OFF | power_state);
					break;
				case 0x16:
					com_wdog_limit &= 0xFF00;
					com_wdog_limit |= datagram[1];
					break;
				case 0x17:
					com_wdog_limit &= 0x00FF;
					com_wdog_limit |= ((UINT16)datagram[1]) << 8;
					break;
				default: ;
			}
			
			com_wdog_count = 0;
		}
		else if(bytes_available && !(temp & 0x80))	//handle read datagram
		{
			datagram[0] = cdc_read_byte();
			
			switch(datagram[0])
			{
				case 0x00:	//device_id[0]
					datagram[0] = '1';
					break;
				case 0x01:	//device_id[1]
					datagram[0] = '6';
					break;
				case 0x02:	//device_id[2]
					datagram[0] = '0';
					break;
				case 0x03:	//device_id[3]
					datagram[0] = '2';
					break;
				
				case 0x04:	//unique_id[0]
					datagram[0] = (UINT8)(*(UINT16 code*)ROM_CHIP_ID_LO);
					break;
				case 0x05:	//unique_id[1]
					datagram[0] = (UINT8)((*(UINT16 code*)ROM_CHIP_ID_LO) >> 8);
					break;
				case 0x06:	//unique_id[2]
					datagram[0] = (UINT8)(*(UINT16 code*)ROM_CHIP_ID_HI);
					break;
				case 0x07:	//unique_id[3]
					datagram[0] = (UINT8)((*(UINT16 code*)ROM_CHIP_ID_HI) >> 8);
					break;
				
				case 0x08:
					datagram[0] = ST7066_NUM_COLUMNS;
					break;
				case 0x09:
					datagram[0] = ST7066_NUM_ROWS;
					break;
				case 0x0A:
					datagram[0] = cursor_col;
					break;
				case 0x0B:
					datagram[0] = cursor_row;
					break;
				
				case 0x0C:
					datagram[0] = contrast;
					break;
				case 0x0D:
					datagram[0] = brightness_r;
					break;
				case 0x0E:
					datagram[0] = brightness_g;
					break;
				case 0x0F:
					datagram[0] = brightness_b;
					break;
				
				case 0x14:
					datagram[0] = power_state;
					break;
				case 0x15:
					datagram[0] = prev_reset_typ | (RESET_KEEP >> 4);
					break;
				case 0x16:
					datagram[0] = (UINT8)com_wdog_limit;
					break;
				case 0x17:
					datagram[0] = (UINT8)(com_wdog_limit >> 8);
				default: ;
			}
			
			cdc_write_byte(datagram[0]);
			com_wdog_count = 0;
		}
		else if(bytes_available)	//datagrams not received in a single transfer are ignored
		{
			cdc_read_bytes(datagram, bytes_available);	//get rid of the extra bytes
		}
		
		if(com_wdog_limit && com_wdog_limit == com_wdog_count)
		{
			rcc_soft_reset();
		}
		
		if(timer_overflow_counts[TIMER_0])
		{
			timer_overflow_counts[TIMER_0] = 0;
			
			if(brightness_g >= pwm_count)
				gpio_set_pin(GPIO_PORT_1, GPIO_PIN_6);
			else
				gpio_clear_pin(GPIO_PORT_1, GPIO_PIN_6);
			
			if(brightness_b >= pwm_count)
				gpio_set_pin(GPIO_PORT_3, GPIO_PIN_3);
			else
				gpio_clear_pin(GPIO_PORT_3, GPIO_PIN_3);
			
			pwm_count += 0x10;
			com_wdog_count += 1;
		}
		
		if(prev_control_line_state != cdc_control_line_state)
		{
			cdc_set_serial_state(cdc_control_line_state & 3);
			prev_control_line_state = cdc_control_line_state;
		}
		
		rcc_reload_wdog(0x00);
	}
}

