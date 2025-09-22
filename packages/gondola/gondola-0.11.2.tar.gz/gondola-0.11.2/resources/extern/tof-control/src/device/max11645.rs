#![allow(unused)]
use crate::constant::*;

use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// Register
const SETUP: u16 = 0x80;
const CONFIG: u16 = 0x00;
// Setup Parameters
const SETUP_VDD_NC_OFF: u16 = 0x00; // Reference Voltage = Vdd, REF = Not Connected, Internal Reference State = Always Off
const SETUP_ER_RI_OFF: u16 = 0x20; // Reference Voltage = External Reference, REF = Reference Input, Internal Reference State = Always Off
const SETUP_IR_NC_OFF: u16 = 0x40; // Reference Voltage = Internal Reference, REF = Not Connected, Internal Reference State = Always Off
const SETUP_IR_NC_ON: u16 = 0x50; // Reference Voltage = Internal Reference, REF = Not Connected, Internal Reference State = Always On
const SETUP_IR_RO_OFF: u16 = 0x60; // Reference Voltage = Internal Reference, REF = Reference Output, Internal Reference State = Always Off
const SETUP_IR_RO_ON: u16 = 0x70; // Reference Voltage = Internal Reference, REF = Reference Output, Internal Reference State = Always On
const SETUP_INT_CLK: u16 = 0x00; // Internal Clock
const SETUP_EXT_CLK: u16 = 0x08; // External Clock
const SETUP_UNI: u16 = 0x00; // Unipolar
const SETUP_BIP: u16 = 0x04; // Bipolar
const SETUP_RST: u16 = 0x00; // Reset
const SETUP_NA: u16 = 0x01; // No Action
                            // Configuration Parameters
const CONFIG_SCAN_0: u16 = 0x00; // Scans up from AIN0 to the input selected by CS0.
const CONFIG_SCAN_1: u16 = 0x20; // Converts the input selected by CS0 eight times.
const CONFIG_SCAN_2: u16 = 0x40; // Reserved. Do not use.
const CONFIG_SCAN_3: u16 = 0x60; // Converts channel selected by CS0.
const CONFIG_DIF: u16 = 0x00; // Differential
const CONFIG_SGL: u16 = 0x01; // Single-ended

pub struct MAX11645 {
    bus: u8,
    address: u16,
}

impl MAX11645 {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn setup(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let setup_reg = SETUP | SETUP_IR_RO_ON | SETUP_INT_CLK | SETUP_UNI | SETUP_RST;

        dev.smbus_write_i2c_block_data(0x00, &setup_reg.to_be_bytes())
    }
    fn config(&self, channel: u8, dev: &mut LinuxI2CDevice) -> u16 {
        let config_reg = CONFIG | CONFIG_SCAN_3 | self.channel_selector(channel) | CONFIG_SGL;
        dev.smbus_write_i2c_block_data(0x00, &config_reg.to_be_bytes())
            .expect("cannot configure MAX11645");

        config_reg
    }
    fn channel_selector(&self, channel: u8) -> u16 {
        let channel_reg = match channel {
            0 => 0x00,
            1 => 0x02,
            _ => 0x00,
        };

        channel_reg
    }
    pub fn read(&self, channel: u8) -> Result<f32, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let config = self.config(channel, &mut dev);
        let voltage_raw = dev.smbus_read_i2c_block_data(config as u8, 2)?;
        let voltage_adc = ((voltage_raw[0] as u16 & 0x0F) << 8) | (voltage_raw[1] as u16 & 0xFF);
        let voltage = voltage_adc as f32 * RB_ADC_REF_VOLTAGE / 4096.0;

        Ok(voltage)
    }
}
