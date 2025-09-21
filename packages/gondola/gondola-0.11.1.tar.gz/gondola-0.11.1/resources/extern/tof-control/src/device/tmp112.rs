#![allow(unused)]
use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// Register
const TEMP: u16 = 0x00; // Temperature Register
const CONFIG: u16 = 0x01; // Configuration Register
const T_LOW: u16 = 0x02; // T Low Register
const T_HIGI: u16 = 0x03; // T High Register
                          // Configuration Register
const CONFIG_CR_025: u16 = 0x0000; // Continuos-Conversion Rate 0.25Hz
const CONFIG_CR_1: u16 = 0x0040; // Continuos-Conversion Rate 1Hz
const CONFIG_CR_4: u16 = 0x0080; // Continuos-Conversion Rate 4Hz, Default
const CONFIG_CR_8: u16 = 0x00C0; // Continuos-Conversion Rate 8Hz
const CONFIG_NM: u16 = 0x0000; // Normal Mode (12 bit), Default
const CONFIG_EM: u16 = 0x0010; // Extended Mode (13 bit)
const CONFIG_OS: u16 = 0x8000; // One-Shot/Conversion Ready Mode
const CONFIG_TM_CM: u16 = 0x0000; // Thermostat Mode, Comparator Mode
const CONFIG_TM_IM: u16 = 0x0200; // Thermostat Mode, Interrupt Mode
const CONFIG_SD_CC: u16 = 0x0000; // Continuous Conversion Mode
const CONFIG_SD_SM: u16 = 0x0100; // Shutdown Mode
const CONFIG_POL: u16 = 0x0400; // Polarity
const CONFIG_F_1: u16 = 0x0000; // Fault Queue, 1 Consecutive Fault
const CONFIG_F_2: u16 = 0x0800; // Fault Queue, 2 Consecutive Faults
const CONFIG_F_4: u16 = 0x1000; // Fault Queue, 4 Consecutive Faults
const CONFIG_F_6: u16 = 0x1800; // Fault Queue, 6 Consecutive Faults
                                // High Limit Register
const T_HIGH_TEMP: u16 = 0x4B0; // 65°C for High Limit
                                // Low Limit Register
const T_LOW_TEMP: u16 = 0x3C0; // 60°C for Low Limit

pub struct TMP112 {
    bus: u8,
    address: u16,
}

impl TMP112 {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn config(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let config_reg = CONFIG_F_1 | CONFIG_TM_CM | CONFIG_SD_CC | CONFIG_CR_4;

        dev.smbus_write_i2c_block_data(CONFIG as u8, &config_reg.to_be_bytes())
    }
    pub fn read(&self) -> Result<f32, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let temp_raw = dev.smbus_read_i2c_block_data(TEMP as u8, 2)?;
        let temp_adc = (((temp_raw[0] as u16) << 4) | ((temp_raw[1] as u16) >> 4)) & 0xFFF;

        Ok(self.adc_to_celsius(temp_adc))
    }
    pub fn read_raw(&self) -> Result<u16, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let temp_raw = dev.smbus_read_i2c_block_data(TEMP as u8, 2)?;
        let temp_adc = (((temp_raw[0] as u16) << 4) | ((temp_raw[1] as u16) >> 4)) & 0xFFF;

        Ok(temp_adc)
    }
    fn adc_to_celsius(&self, mut adc: u16) -> f32 {
        let mut sign: f32 = 1.0;
        if adc >= 0x800 {
            sign = -1.0;
            adc = 0xFFF - adc;
        }

        sign * adc as f32 * 0.0625
    }
}
