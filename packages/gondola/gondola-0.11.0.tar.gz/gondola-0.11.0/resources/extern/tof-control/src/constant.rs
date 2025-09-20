#![allow(unused)]
// I2C Options
pub const I2C_BUS: u8 = 0;

// I2C Options for Readout Board
pub const RB_PCA9548A_ADDRESS_1: u16 = 0x75;
pub const RB_PCA9548A_ADDRESS_2: u16 = 0x77;

// PCA9548A_ADDRESS_1
pub const RB_DRS_TMP112_ADDRESS: u16 = 0x48;
pub const RB_DRS_TMP112_CHANNEL: u8 = 2;
// PCA9548A_ADDRESS_2
pub const RB_CLK_TMP112_ADDRESS: u16 = 0x4B;
pub const RB_CLK_TMP112_CHANNEL: u8 = 0;
pub const RB_ADC_TMP112_ADDRESS: u16 = 0x4A;
pub const RB_ADC_TMP112_CHANNEL: u8 = 4;

// PCA9548A_ADDRESS_1
pub const RB_DRS_DVDD_INA226_ADDRESS: u16 = 0x4E;
pub const RB_DRS_DVDD_INA226_CHANNEL: u8 = 3;
pub const RB_DRS_DVDD_INA226_RSHUNT: f32 = 0.1;
pub const RB_DRS_DVDD_INA226_MEC: f32 = 0.1;

pub const RB_P3V3_INA226_ADDRESS: u16 = 0x44;
pub const RB_P3V3_INA226_CHANNEL: u8 = 4;
pub const RB_P3V3_INA226_RSHUNT: f32 = 0.039;
pub const RB_P3V3_INA226_MEC: f32 = 0.75;

pub const RB_ZYNQ_INA226_ADDRESS: u16 = 0x41;
pub const RB_ZYNQ_INA226_CHANNEL: u8 = 5;
pub const RB_ZYNQ_INA226_RSHUNT: f32 = 0.039;
pub const RB_ZYNQ_INA226_MEC: f32 = 0.75;

pub const RB_P3V5_INA226_ADDRESS: u16 = 0x43;
pub const RB_P3V5_INA226_CHANNEL: u8 = 7;
pub const RB_P3V5_INA226_RSHUNT: f32 = 0.039;
pub const RB_P3V5_INA226_MEC: f32 = 0.75;

// PCA9548A_ADDRESS_2
pub const RB_ADC_DVDD_INA226_ADDRESS: u16 = 0x42;
pub const RB_ADC_DVDD_INA226_CHANNEL: u8 = 3;
pub const RB_ADC_DVDD_INA226_RSHUNT: f32 = 0.1;
pub const RB_ADC_DVDD_INA226_MEC: f32 = 0.01;

pub const RB_ADC_AVDD_INA226_ADDRESS: u16 = 0x4F;
pub const RB_ADC_AVDD_INA226_CHANNEL: u8 = 5;
pub const RB_ADC_AVDD_INA226_RSHUNT: f32 = 0.1;
pub const RB_ADC_AVDD_INA226_MEC: f32 = 0.075;

pub const RB_DRS_AVDD_INA226_ADDRESS: u16 = 0x40;
pub const RB_DRS_AVDD_INA226_CHANNEL: u8 = 6;
pub const RB_DRS_AVDD_INA226_RSHUNT: f32 = 0.1;
pub const RB_DRS_AVDD_INA226_MEC: f32 = 0.025;

// PCA9548A_ADDRESS_1
pub const RB_LIS3MDLTR_ADDRESS: u16 = 0x1E;
pub const RB_LIS3MDLTR_CHANNEL: u8 = 1;

// PCA9548A_ADDRESS_1
pub const RB_BME280_ADDRESS: u16 = 0x76;
pub const RB_BME280_CHANNEL: u8 = 0;

// PCA9548A_ADDRESS_1
pub const RB_ADC_REF_VOLTAGE: f32 = 2.048;
pub const RB_MAX11645_ADDRESS: u16 = 0x36;
pub const RB_MAX11645_CHANNEL: u8 = 6;

pub const RB_N1V5_VOLTAGE_INA200_CHANNEL: u8 = 1;
pub const RB_N1V5_CURRENT_INA200_CHANNEL: u8 = 0;

// Clock Synthesizer (SI5345B)
// PCA9548A_ADDRESS_2
pub const RB_SI5345B_ADDRESS: u16 = 0x68;
pub const RB_SI5345B_CHANNEL: u8 = 1;

// GPIO Expander (CY8C9560A)
// PCA9548A_ADDRESS_2
pub const RB_CY8C9560A_ADDRESS: u16 = 0x20;
pub const RB_CY8C9560A_EEPROM_ADDRESS: u16 = 0x50;
pub const RB_CY8C9560A_CHANNEL: u8 = 7;

/// DAC (AD5675)
// PCA9548A_ADDRESS_2
pub const RB_AD5675_ADDRESS: u16 = 0xC;
pub const RB_AD5675_CHANNEL: u8 = 2;

/// RB Internal Address Table
pub const RB_UIO0: &'static str = "/dev/uio0";

/// DRS.CHIP (Registers for configuring the DRS ASIC Directly)
pub const DRS_PLL_LOCK: u32 = 0x00; // Bits: 4, Perm: r, Description: DRS PLL Locked
pub const LOSS_OF_LOCK: u32 = 0x10; // Bits: 0, Perm: r, Description: Raw reading of LOL signal
pub const LOSS_OF_LOCK_STABLE: u32 = 0x10; // Bits: 1, Perm: r, Description: Loss of lock stable over the past ~second
/// DRS.FPGA.XADC (Zynq XADC)
pub const RB_TEMP: u32 = 0xA0; // Bits: [11:0], Perm: r, XADC Temperature
/// DRS.FPGA (FPGA Status)
pub const BOARD_ID: u32 = 0xA8; // Bits: [7:0], Perm: rw, Board ID Number
pub const DRS_TEMP: u32 = 0xAC; // Bits: [15:0], Perm: rw, Copy of the I2C DRS temperature reading
pub const RAT_HOUSEKEEPING: u32 = 0xB0; // Bits: [31:0], Perm: rw, 32 bit RAT housekeeping data. Meaning is software defined.
/// DRS.DAQ (DAQ)
pub const DAQ_FRAGMENT_EN: u32 = 0xC4; // Bits: 0, Perm: rw, 1 to enable daq fragments (header only packets) when the DRS is busy
/// DRS.READOUT (Registers for configuring the readout state machine)
pub const EN_SPIKE_REMOVAL: u32 = 0x40; // Bits: 22, Perm: rw, Description: set 1 to enable spike removal
pub const READOUT_MASK: u32 = 0x44; // Bits: [8:0], Perm: rw, 8 bit mask, set a bit to 1 to enable readout of that channel. 9th is auto-read if any channel is enabled and AUTO_9TH_CHANNEL set to 1
pub const START: u32 = 0x48; // Bits: 0, Perm: w, Description: Write 1 to take the state machine out of idle mode
/// DRS.TRIGGER
pub const TRIGGER_ENABLE: u32 = 0x11C; // Bits: 0, Perm: rw, Description: Set to 0 to stop all triggers. 1 to enable triggers.
pub const MT_EVENT_CNT: u32 = 0x120; // Bits: [31:0], Perm: r, Description: Recevied event counter
pub const MT_TRIGGER_RATE: u32 = 0x124; // Bits: [31:0], Perm: r, Description: Rate of triggers received from the MTB in Hz
/// DRS.COUNTERS
pub const CNT_LOST_EVENT: u32 = 0x150; // Bits: [31:16], Perm: r, Description: Number of trigger lost due to deadtime
pub const CNT_EVENT: u32 = 0x154; // Bits: [31:0], Perm: r, Description: Number of triggers received
pub const TRIGGER_RATE: u32 = 0x158; // Bits: [31:0], Perm: r, Description: Rate of triggers in Hz
pub const LOST_TRIGGER_RATE: u32 = 0x15C; // Bits: [31:0], Perm: r, Description: Rate of lost triggers in Hz
/// DRS.HOG (HOG Parameters)
pub const GLOBAL_VER: u32 = 0x188; // Bits: [31:0], Perm: r, Description: HOG Global Version
pub const GLOBAL_SHA: u32 = 0x18C; // Bits: [31:0], Perm: r, Description: HOG Global SHA

// I2C Options for Power Board
pub const PB_PCA9548A_ADDRESS: u16 = 0x70;

pub const PB_TMP1075_CHANNEL: u8 = 4;
pub const PB_PDS_TMP1075_ADDRESS: u16 = 0x48;
pub const PB_PAS_TMP1075_ADDRESS: u16 = 0x49;
pub const PB_NAS_TMP1075_ADDRESS: u16 = 0x4A;
pub const PB_SHV_TMP1075_ADDRESS: u16 = 0x4B;

pub const PB_P3V6_PA_INA226_ADDRESS: u16 = 0x46;
pub const PB_P3V6_PA_INA226_CHANNEL: u8 = 6;
pub const PB_P3V6_PA_INA226_RSHUNT: f32 = 0.1;
pub const PB_P3V6_PA_INA226_MEC: f32 = 0.35;
pub const PB_N1V6_PA_VOLTAGE_INA201_CHANNEL: u8 = 3;
pub const PB_N1V6_PA_CURRENT_INA201_CHANNEL: u8 = 2;
pub const PB_LTB_INA219_CHANNEL: u8 = 5;
pub const PB_P3V4F_LTB_INA219_ADDRESS: u16 = 0x46;
pub const PB_P3V4F_LTB_INA219_RSHUNT: f32 = 0.1;
pub const PB_P3V4F_LTB_INA219_MEC: f32 = 0.05;
pub const PB_P3V4D_LTB_INA219_ADDRESS: u16 = 0x47;
pub const PB_P3V4D_LTB_INA219_RSHUNT: f32 = 0.1;
pub const PB_P3V4D_LTB_INA219_MEC: f32 = 0.075;
pub const PB_P3V6_LTB_INA219_ADDRESS: u16 = 0x4C;
pub const PB_P3V6_LTB_INA219_RSHUNT: f32 = 0.1;
pub const PB_P3V6_LTB_INA219_MEC: f32 = 0.25;
pub const PB_N1V6_LTB_VOLTAGE_INA202_CHANNEL: u8 = 3;
pub const PB_N1V6_LTB_CURRENT_INA202_CHANNEL: u8 = 2;

pub const PB_ADC_REF_VOLTAGE: f32 = 3.0;
pub const PB_ADC_1_CHANNEL: u8 = 1;
pub const PB_ADC_2_CHANNEL: u8 = 3;
pub const PB_MAX11615_ADDRESS: u16 = 0x33;
pub const PB_MAX11617_ADDRESS: u16 = 0x35;

pub const PB_DAC_REF_VOLTAGE: f32 = 3.0;
pub const PB_DAC_1_CHANNEL: u8 = 0;
pub const PB_DAC_2_CHANNEL: u8 = 2;
pub const PB_MAX5825_ADDRESS: u16 = 0x1F;

// LTB Power
pub const PB_MAX7320_CHANNEL: u8 = 7;
pub const PB_MAX7320_ADDRESS: u16 = 0x59;

// I2C Options for Local Trigger Board
// Trenz Board
pub const LTB_TRENZ_ADDRESS: u16 = 0x3C;
pub const LTB_TRENZ_TEMP_OFFSET: u16 = 0x00;
// LTB Temperature Sensor (TMP112)
pub const LTB_TMP112_ADDRESS: u16 = 0x49;
// LTB DAC (MAX5815)
pub const LTB_DAC_REF_VOLTAGE: f32 = 2.5;
pub const LTB_MAX5815_ADDRESS: u16 = 0x1A;
pub const LTB_DAC_THRESHOLD_0: f32 = 40.0; // 40.0mV
                                           // pub const LTB_DAC_THRESHOLD_0: f32 = 50.0; // 50.0mV
pub const LTB_DAC_THRESHOLD_1: f32 = 32.0; // 32.0mV
                                           // pub const LTB_DAC_THRESHOLD_1: f32 = 50.0; // 50.0mV
pub const LTB_DAC_THRESHOLD_2: f32 = 375.0; // 375.0mV
                                            // pub const LTB_DAC_THRESHOLD_2: f32 = 150.0; // 150.0mV

// I2C Options for Preamp Board
pub const PA_TEMP_1_CHNANNEL: u8 = 7; // ADC 1, MAX11615
pub const PA_TEMP_2_CHNANNEL: u8 = 6; // ADC 1, MAX11615
pub const PA_TEMP_3_CHNANNEL: u8 = 5; // ADC 1, MAX11615
pub const PA_TEMP_4_CHNANNEL: u8 = 4; // ADC 1, MAX11615
pub const PA_TEMP_5_CHNANNEL: u8 = 4; // ADC 1, MAX11617
pub const PA_TEMP_6_CHNANNEL: u8 = 5; // ADC 1, MAX11617
pub const PA_TEMP_7_CHNANNEL: u8 = 6; // ADC 1, MAX11617
pub const PA_TEMP_8_CHNANNEL: u8 = 7; // ADC 1, MAX11617
pub const PA_TEMP_9_CHNANNEL: u8 = 7; // ADC 2, MAX11615
pub const PA_TEMP_10_CHNANNEL: u8 = 6; // ADC 2, MAX11615
pub const PA_TEMP_11_CHNANNEL: u8 = 5; // ADC 2, MAX11615
pub const PA_TEMP_12_CHNANNEL: u8 = 4; // ADC 3, MAX11615
pub const PA_TEMP_13_CHNANNEL: u8 = 4; // ADC 2, MAX11617
pub const PA_TEMP_14_CHNANNEL: u8 = 5; // ADC 2, MAX11617
pub const PA_TEMP_15_CHNANNEL: u8 = 6; // ADC 2, MAX11617
pub const PA_TEMP_16_CHNANNEL: u8 = 7; // ADC 2, MAX11617

pub const PA_SEN_1_CHANNEL: u8 = 3; // ADC 1, MAX11615
pub const PA_SEN_2_CHANNEL: u8 = 2; // ADC 1, MAX11615
pub const PA_SEN_3_CHANNEL: u8 = 1; // ADC 1, MAX11615
pub const PA_SEN_4_CHANNEL: u8 = 0; // ADC 1, MAX11615
pub const PA_SEN_5_CHANNEL: u8 = 10; // ADC 1, MAX11617
pub const PA_SEN_6_CHANNEL: u8 = 9; // ADC 1, MAX11617
pub const PA_SEN_7_CHANNEL: u8 = 8; // ADC 1, MAX11617
pub const PA_SEN_8_CHANNEL: u8 = 0; // ADC 1, MAX11617
pub const PA_SEN_9_CHANNEL: u8 = 3; // ADC 2, MAX11615
pub const PA_SEN_10_CHANNEL: u8 = 2; // ADC 2, MAX11615
pub const PA_SEN_11_CHANNEL: u8 = 1; // ADC 2, MAX11615
pub const PA_SEN_12_CHANNEL: u8 = 0; // ADC 2, MAX11615
pub const PA_SEN_13_CHANNEL: u8 = 10; // ADC 2, MAX11617
pub const PA_SEN_14_CHANNEL: u8 = 9; // ADC 2, MAX11617
pub const PA_SEN_15_CHANNEL: u8 = 8; // ADC 2, MAX11617
pub const PA_SEN_16_CHANNEL: u8 = 0; // ADC 2, MAX11617

pub const PA_DAC_1_CHANNEL: u8 = 0; // DAC1, MAX5825
pub const PA_DAC_2_CHANNEL: u8 = 1; // DAC1, MAX5825
pub const PA_DAC_3_CHANNEL: u8 = 2; // DAC1, MAX5825
pub const PA_DAC_4_CHANNEL: u8 = 3; // DAC1, MAX5825
pub const PA_DAC_5_CHANNEL: u8 = 4; // DAC1, MAX5825
pub const PA_DAC_6_CHANNEL: u8 = 5; // DAC1, MAX5825
pub const PA_DAC_7_CHANNEL: u8 = 6; // DAC1, MAX5825
pub const PA_DAC_8_CHANNEL: u8 = 7; // DAC1, MAX5825
pub const PA_DAC_9_CHANNEL: u8 = 0; // DAC2, MAX5825
pub const PA_DAC_10_CHANNEL: u8 = 1; // DAC2, MAX5825
pub const PA_DAC_11_CHANNEL: u8 = 2; // DAC2, MAX5825
pub const PA_DAC_12_CHANNEL: u8 = 3; // DAC2, MAX5825
pub const PA_DAC_13_CHANNEL: u8 = 4; // DAC2, MAX5825
pub const PA_DAC_14_CHANNEL: u8 = 5; // DAC2, MAX5825
pub const PA_DAC_15_CHANNEL: u8 = 6; // DAC2, MAX5825
pub const PA_DAC_16_CHANNEL: u8 = 7; // DAC2, MAX5825

pub const PA_DEFAULT_BIAS: f32 = 58.0;

// I2C Options for CPC
pub const CPC_I2C_BUS: u8 = 2;

pub const CPC_TMP1075_ADDRESS: u16 = 0x48;

pub const CPC_INA219_ADDRESS: u16 = 0x46;
pub const CPC_INA219_RSHUNT: f32 = 0.03;
pub const CPC_INA219_MEC: f32 = 1.25;

pub const CPC_MAX7320_ADDRESS: u16 = 0x59;

// I2C Options for TCPC
pub const TCPC_TMP1075_ADDRESS: u16 = 0x48;

pub const TCPC_INA219_ADDRESS: u16 = 0x46;
pub const TCPC_INA219_RSHUNT: f32 = 0.03;
pub const TCPC_INA219_MEC: f32 = 1.25;

pub const TCPC_MAX7320_ADDRESS: u16 = 0x59;

// Switch Constants
pub const SWITCH1_ADDRESS: &str = "10.0.1.11:161";
pub const SWITCH2_ADDRESS: &str = "10.0.1.12:161";
pub const SWITCH3_ADDRESS: &str = "10.0.1.13:161";
pub const SWITCH4_ADDRESS: &str = "10.0.1.14:161";
