#![allow(unused)]
use crate::constant::*;

use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

pub struct MAX7320 {
    bus: u8,
    address: u16,
}

impl MAX7320 {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn output_on_0_3(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte(0x0F)
    }
    pub fn output_off_all(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte(0x00)
    }
}
