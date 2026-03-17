#include "CH552.H"
#include "CH552_RCC.h"
#include "CH552_TIMER.h"
#include "CH552_GPIO.h"
#include "CH552_USB_CDC.h"
#include "CH552_UART.h"
#include "CH552_ST7066.h"

#define  BAUD_RATE  125000ul

char code str_rst_typ[] = "reset type:";

char code str_cdc_last_data_time[] = "cdc_last_data_time:";
char code str_cdc_last_status_time[] = "cdc_last_status_time:";
char code str_cdc_tx_enabled[] = "cdc_tx_enabled:";
//char code str_cdc_rx_enabled[] = "cdc_rx_enabled:";

char code str_ep2_read_select[] = "ep2_read_select:";
char code str_ep2_t0_zlp[] = "ep2_t0_zlp:";
char code str_ep2_t0_num_bytes[] = "ep2_t0_num_bytes:";
char code str_ep2_t0_read_offset[] = "ep2_t0_read_offset:";
char code str_ep2_t1_zlp[] = "ep2_t1_zlp:";
char code str_ep2_t1_num_bytes[] = "ep2_t1_num_bytes:";
char code str_ep2_t1_read_offset[] = "ep2_t1_read_offset:";

char code str_ep3_wip[] = "ep3_wip:";
char code str_ep3_write_select[] = "ep3_write_select:";
char code str_ep3_t0_num_bytes[] = "ep3_t0_num_bytes:";
char code str_ep3_t1_num_bytes[] = "ep3_t1_num_bytes:";

char code str_cdc_setup_req[] = "cdc_setup_req:";
char code str_cdc_setup_type[] = "cdc_setup_type:";
char code str_cdc_setup_len[] = "cdc_setup_len:";
char code str_descriptor_ptr[] = "descriptor_ptr:";
#if CDC_USE_UNIQUE_ID
char code str_cdc_string_serial_offset[] = "cdc_string_serial_offset:";
#endif

char code str_usb_int_en[] = "USB_INT_EN:";
char code str_dev_ad[] = "USB_DEV_AD:";
char code str_uep0_t_len[] = "UEP0_T_LEN:";
char code str_uep1_t_len[] = "UEP1_T_LEN:";
char code str_uep2_t_len[] = "UEP2_T_LEN:";
char code str_uep3_t_len[] = "UEP3_T_LEN:";
char code str_usb_rx_len[] = "USB_RX_LEN:";
char code str_uep0_ctrl[] = "UEP0_CTRL:";
char code str_uep1_ctrl[] = "UEP1_CTRL:";
char code str_uep2_ctrl[] = "UEP2_CTRL:";
char code str_uep3_ctrl[] = "UEP3_CTRL:";
char code str_usb_int_fg[] = "USB_INT_FG:";
char code str_usb_int_st[] = "USB_INT_ST:";
char code str_usb_mis_st[] = "USB_MIS_ST:";

extern UINT16 cdc_last_data_time;
extern UINT16 cdc_last_status_time;
extern volatile UINT8 cdc_tx_enabled;
//extern volatile UINT8 cdc_rx_enabled;

extern UINT8 ep2_read_select;
extern volatile UINT8 ep2_t0_zlp;	//set when a ZLP is received in t0
extern volatile UINT8 ep2_t0_num_bytes;
extern UINT8 ep2_t0_read_offset;
extern volatile UINT8 ep2_t1_zlp;
extern volatile UINT8 ep2_t1_num_bytes;
extern UINT8 ep2_t1_read_offset;

extern volatile UINT8 ep3_wip;
extern volatile UINT8 ep3_write_select;
extern volatile UINT8 ep3_t0_num_bytes;
extern volatile UINT8 ep3_t1_num_bytes;

extern UINT8 cdc_setup_req;
extern UINT8 cdc_setup_type;
extern UINT16 cdc_setup_len;
extern UINT8 code* descriptor_ptr;
#if CDC_USE_UNIQUE_ID
extern UINT8 cdc_string_serial_offset;
#endif

//Pins:
// LCD_E = P14
// LCD_DATA = P15
// G_PWM = P16
// LCD_CLK = P17
// RXD0 = P30
// TXD0 = P31
// LCD_RS = P32
// B_PWM = P33
// UDP = P36
// UDM = P37

char code hex_table[16] = {0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46};

void byte_to_hex(UINT8 value, char* buff)
{
	buff[0] = hex_table[(value >> 4) & 0x0F];
	buff[1] = hex_table[(value) & 0x0f];
	buff[2] = '\n';
	buff[3] = '\0';
}

void word_to_hex(UINT16 value, char* buff)
{
	buff[0] = hex_table[value >> 12];
	buff[1] = hex_table[(value >> 8) & 0x0F];
	buff[2] = hex_table[(value >> 4) & 0x0F];
	buff[3] = hex_table[value & 0x0F];
	buff[4] = '\n';
	buff[5] = '\0';
}

void cdc_scrutinize()
{
	char str_buf[6];
	
	//Reset type
	byte_to_hex(rcc_get_rst_typ(), str_buf);
	uart_write_string(UART_0, str_rst_typ);
	uart_write_string(UART_0, str_buf);
	
	//CDC variables
	word_to_hex(cdc_last_data_time, str_buf);
	uart_write_string(UART_0, str_cdc_last_data_time);
	uart_write_string(UART_0, str_buf);
	
	word_to_hex(cdc_last_status_time, str_buf);
	uart_write_string(UART_0, str_cdc_last_status_time);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(cdc_tx_enabled, str_buf);
	uart_write_string(UART_0, str_cdc_tx_enabled);
	uart_write_string(UART_0, str_buf);
	
	/*byte_to_hex(cdc_rx_enabled, str_buf);
	uart_write_string(UART_0, str_cdc_rx_enabled);
	uart_write_string(UART_0, str_buf);*/

	byte_to_hex(ep2_read_select, str_buf);
	uart_write_string(UART_0, str_ep2_read_select);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep2_t0_zlp, str_buf);
	uart_write_string(UART_0, str_ep2_t0_zlp);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep2_t0_num_bytes, str_buf);
	uart_write_string(UART_0, str_ep2_t0_num_bytes);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep2_t0_read_offset, str_buf);
	uart_write_string(UART_0, str_ep2_t0_read_offset);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep2_t1_zlp, str_buf);
	uart_write_string(UART_0, str_ep2_t1_zlp);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep2_t1_num_bytes, str_buf);
	uart_write_string(UART_0, str_ep2_t1_num_bytes);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep2_t1_read_offset, str_buf);
	uart_write_string(UART_0, str_ep2_t1_read_offset);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep3_wip, str_buf);
	uart_write_string(UART_0, str_ep3_wip);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep3_write_select, str_buf);
	uart_write_string(UART_0, str_ep3_write_select);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep3_t0_num_bytes, str_buf);
	uart_write_string(UART_0, str_ep3_t0_num_bytes);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(ep3_t1_num_bytes, str_buf);
	uart_write_string(UART_0, str_ep3_t1_num_bytes);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(cdc_setup_req, str_buf);
	uart_write_string(UART_0, str_cdc_setup_req);
	uart_write_string(UART_0, str_buf);

	byte_to_hex(cdc_setup_type, str_buf);
	uart_write_string(UART_0, str_cdc_setup_type);
	uart_write_string(UART_0, str_buf);

	word_to_hex(cdc_setup_len, str_buf);
	uart_write_string(UART_0, str_cdc_setup_len);
	uart_write_string(UART_0, str_buf);

	word_to_hex((UINT16)descriptor_ptr, str_buf);
	uart_write_string(UART_0, str_descriptor_ptr);
	uart_write_string(UART_0, str_buf);

#if CDC_USE_UNIQUE_ID
	byte_to_hex(cdc_string_serial_offset, str_buf);
	uart_write_string(UART_0, str_cdc_string_serial_offset);
	uart_write_string(UART_0, str_buf);
#endif

	//USB registers
	byte_to_hex(USB_INT_EN, str_buf);
	uart_write_string(UART_0, str_usb_int_en);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(USB_DEV_AD, str_buf);
	uart_write_string(UART_0, str_dev_ad);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(UEP0_T_LEN, str_buf);
	uart_write_string(UART_0, str_uep0_t_len);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(UEP1_T_LEN, str_buf);
	uart_write_string(UART_0, str_uep1_t_len);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(UEP2_T_LEN, str_buf);
	uart_write_string(UART_0, str_uep2_t_len);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(UEP3_T_LEN, str_buf);
	uart_write_string(UART_0, str_uep3_t_len);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(USB_RX_LEN, str_buf);
	uart_write_string(UART_0, str_usb_rx_len);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(UEP0_CTRL, str_buf);
	uart_write_string(UART_0, str_uep0_ctrl);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(UEP1_CTRL, str_buf);
	uart_write_string(UART_0, str_uep1_ctrl);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(UEP2_CTRL, str_buf);
	uart_write_string(UART_0, str_uep2_ctrl);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(UEP3_CTRL, str_buf);
	uart_write_string(UART_0, str_uep3_ctrl);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(USB_INT_FG, str_buf);
	uart_write_string(UART_0, str_usb_int_fg);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(USB_INT_ST, str_buf);
	uart_write_string(UART_0, str_usb_int_st);
	uart_write_string(UART_0, str_buf);
	
	byte_to_hex(USB_MIS_ST, str_buf);
	uart_write_string(UART_0, str_usb_mis_st);
	uart_write_string(UART_0, str_buf);
}

int main()
{
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
	
	rcc_set_clk_freq(RCC_CLK_FREQ_24M);
	
	gpio_set_mode(GPIO_MODE_PP, GPIO_PORT_1, GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7);	//LCD_E, LCD_DATA, G_PWM, CLK_CLK
	gpio_set_mode(GPIO_MODE_INPUT, GPIO_PORT_3, GPIO_PIN_0);	//RXD0
	gpio_set_mode(GPIO_MODE_PP, GPIO_PORT_3, GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3);	//TXD0, LCD_RS, B_PWM
	gpio_clear_pin(GPIO_PORT_1, GPIO_PIN_4);
	gpio_clear_pin(GPIO_PORT_3, GPIO_PIN_2);
	
	uart0_init(TIMER_1, BAUD_RATE, UART_0_P30_P31);
	timer_init(TIMER_0, NULL);
	timer_set_period(TIMER_0, FREQ_SYS / 1000ul);	//period is 1ms
	EA = 1;	//enable interupts
	E_DIS = 0;
	
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
					break;
				case 0x0D:
					brightness_r = datagram[1];
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
				default: ;
			}
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
					datagram[0] = 16;
					break;
				case 0x09:
					datagram[0] = 2;
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
				default: ;
			}
			
			cdc_write_byte(datagram[0]);
		}
		else if(bytes_available)	//datagrams not received in a single transfer are ignored
		{
			cdc_read_bytes(datagram, bytes_available);	//get rid of the extra bytes
		}
		
		if(uart_bytes_available(UART_0))
		{
			if(uart_read_byte(UART_0) == 'S')
			{
				rcc_reload_wdog(0x00);
				rcc_set_wdog_rst_en(RCC_WDOG_DISABLED);
				cdc_scrutinize();
				rcc_reload_wdog(0x00);
				rcc_set_wdog_rst_en(RCC_WDOG_ENABLED);
			}
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
		}
		
		if(prev_control_line_state != cdc_control_line_state)
		{
			cdc_set_serial_state(cdc_control_line_state & 3);
			prev_control_line_state = cdc_control_line_state;
		}
		
		rcc_reload_wdog(0x00);
	}
}

