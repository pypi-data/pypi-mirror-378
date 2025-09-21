#![allow(unused)]
use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// Register
const TEMP: u16 = 0x00; // Temperature Result Register
const CFGR: u16 = 0x01; // Configuration Register
const LLIM: u16 = 0x02; // Low Limit Register
const HLIM: u16 = 0x03; // High Limit Register
                        // Configuration Register
const CONFIG_OS: u16 = 0x80A0; // One-shot conversion mode
const CONFIG_R_35: u16 = 0x60A0; // 35 ms conversion rate (Read-only)
const CONFIG_F_1: u16 = 0x00A0; // 1 fault
const CONFIG_F_2: u16 = 0x08A0; // 2 fault
const CONFIG_F_4: u16 = 0x10A0; // 4 fault
const CONFIG_F_6: u16 = 0x18A0; // 6 fault
const CONFIG_POL_L: u16 = 0x00A0; // Active low ALERT pin
const CONFIG_POL_H: u16 = 0x04A0; // Active high ALERT pin
const CONFIG_TM_CM: u16 = 0x00A0; // ALERT pin functions in comparator mode
const CONFIG_TM_IM: u16 = 0x02A0; // ALERT pin functions in interrupt mode
const CONFIG_SD_CC: u16 = 0x00A0; // Device is in continuos conversion
const CONFIG_SD_SM: u16 = 0x01A0; // Device is in shutdown conversion

pub struct TMP1075 {
    bus: u8,
    address: u16,
}

impl TMP1075 {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn config(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let config_reg = CONFIG_R_35 | CONFIG_F_1 | CONFIG_POL_L | CONFIG_TM_CM | CONFIG_SD_CC;

        dev.smbus_write_i2c_block_data(CFGR as u8, &config_reg.to_be_bytes())
    }
    pub fn read(&self) -> Result<f32, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let temp_raw = dev.smbus_read_i2c_block_data(TEMP as u8, 2)?;
        let mut temp_adc = (((temp_raw[0] as u16) << 4) | ((temp_raw[1] as u16) >> 4)) & 0xFFF;

        Ok(self.adc_to_celsius(temp_adc))
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
