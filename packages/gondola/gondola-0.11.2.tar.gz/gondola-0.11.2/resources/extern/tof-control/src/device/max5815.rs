#![allow(unused)]
use crate::constant::*;

use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// Readback Register
const DEVICE_INFO: u16 = 0xFF;
const READBACK_CODEN: u16 = 0x00;
const READBACK_DACN: u16 = 0x10;
const READBACK_CODEA: u16 = 0x80;
const READBACK_DACA: u16 = 0x81;
const READBACK_POWER: u16 = 0x40;
// Configuration Register
const REF_2_5V: u16 = 0x75;
const SW_CLEAR: u16 = 0x50;
const SW_RESET: u16 = 0x51;
// DAC Register
const CODEN_LOADN: u16 = 0x30;
const LOAD_ALL: u16 = 0x81;

pub struct MAX5815 {
    bus: u8,
    address: u16,
}

impl MAX5815 {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn configure(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        self.set_reference_voltage(&mut dev)?;

        Ok(())
    }
    fn set_reference_voltage(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        dev.smbus_write_i2c_block_data(REF_2_5V as u8, &[0x00, 0x00])
    }
    pub fn read_device_info(&self) -> Result<(u8, u8, u8), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let device_info = dev.smbus_read_i2c_block_data(DEVICE_INFO as u8, 2)?;
        let device_id = device_info[0];
        let rev_id = (device_info[1] & 0x1C) >> 2;
        let ref_mode = (device_info[1] & 0x03);

        Ok((device_id, rev_id, ref_mode))
    }
    pub fn read_coden(&self, channel: u8) -> Result<(u16), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let coden_buf = dev.smbus_read_i2c_block_data(((READBACK_CODEN as u8) | channel), 2)?;
        let coden = ((coden_buf[0] as u16) << 4) | (((coden_buf[1] as u16) & 0xF0) >> 4);

        Ok((coden))
    }
    pub fn read_codea(&self) -> Result<(u16), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let codea_buf = dev.smbus_read_i2c_block_data(READBACK_CODEA as u8, 2)?;
        let codea = ((codea_buf[0] as u16) << 4) | (((codea_buf[1] as u16) & 0xF0) >> 4);

        Ok((codea))
    }
    pub fn read_dacn(&self, channel: u8) -> Result<(u16), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let dacn_buf = dev.smbus_read_i2c_block_data(((READBACK_DACN as u8) | channel), 2)?;
        let dacn = ((dacn_buf[0] as u16) << 4) | (((dacn_buf[1] as u16) & 0xF0) >> 4);

        Ok((dacn))
    }
    pub fn read_daca(&self) -> Result<(u16), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let daca_buf = dev.smbus_read_i2c_block_data(READBACK_DACA as u8, 2)?;
        let daca = ((daca_buf[0] as u16) << 4) | (((daca_buf[1] as u16) & 0xF0) >> 4);

        Ok((daca))
    }
    pub fn reset_dac(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_i2c_block_data(SW_CLEAR as u8, &[0x00, 0x00]);

        Ok(())
    }
    pub fn coden_loadn(&self, channel: u8, adc: u16) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let code_register_data = [((adc >> 4) as u8) & 0xFF, ((adc & 0x0F) as u8) << 4];
        dev.smbus_write_i2c_block_data(((CODEN_LOADN as u8) | channel), &code_register_data)
    }
}
