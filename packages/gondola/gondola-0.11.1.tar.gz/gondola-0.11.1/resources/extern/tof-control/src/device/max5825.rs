#![allow(unused)]
use crate::constant::*;

use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// Readback Register
const DEVICE_INFO: u16 = 0xFF;
const READBACK_CODEN: u16 = 0x80;
const READBACK_DACN: u16 = 0x90;
// Configuration Register
const REF_EXT: u16 = 0x20;
const SW_CLEAR: u16 = 0x34;
// DAC Register
const CODEN_LOADN: u16 = 0xB0;

pub struct MAX5825 {
    bus: u8,
    address: u16,
}

impl MAX5825 {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn configure(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        self.set_reference_voltage(&mut dev)?;

        Ok(())
    }
    pub fn reset_dac(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let sw_clear_data: [u8; 2] = [0x96, 0x30];
        dev.smbus_write_i2c_block_data(SW_CLEAR as u8, &sw_clear_data);

        Ok(())
    }
    fn set_reference_voltage(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        dev.smbus_write_byte(REF_EXT as u8)
    }
    pub fn read_device_info(&self) -> Result<(u8, u8, u8, u8, u8), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let device_info = dev.smbus_read_i2c_block_data(DEVICE_INFO as u8, 2)?;
        let wd_enabled = (device_info[0] & 0x80) >> 7;
        let ref_mode = (device_info[0] & 0x70) >> 4;
        let clr_enabled = (device_info[0] & 0x08) >> 3;
        let rev_id = device_info[0] & 0x07;
        let device_id = device_info[1];

        Ok((wd_enabled, ref_mode, clr_enabled, rev_id, device_id))
    }
    pub fn read_coden(&self, channel: u8) -> Result<(u16), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let coden_buf = dev.smbus_read_i2c_block_data(((READBACK_CODEN as u8) | channel), 2)?;
        let coden = ((coden_buf[0] as u16) << 4) | (((coden_buf[1] as u16) & 0xF0) >> 4);

        Ok((coden))
    }
    pub fn read_dacn(&self, channel: u8) -> Result<(u16), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let dacn_buf = dev.smbus_read_i2c_block_data(((READBACK_DACN as u8) | channel), 2)?;
        let dacn = ((dacn_buf[0] as u16) << 4) | (((dacn_buf[1] as u16) & 0xF0) >> 4);

        Ok((dacn))
    }
    pub fn coden_loadn(&self, channel: u8, adc: u16) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let code_register_data = [((adc >> 4) as u8) & 0xFF, ((adc & 0x0F) as u8) << 4];
        dev.smbus_write_i2c_block_data(((CODEN_LOADN as u8) | channel), &code_register_data)?;

        Ok(())
    }
}
