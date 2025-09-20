use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

pub struct PCA9548A {
    bus: u8,
    address: u16,
}

impl PCA9548A {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn select(&self, channel: u8) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        dev.smbus_write_byte_data(
            0x00,
            match channel {
                0 => 0x01,
                1 => 0x02,
                2 => 0x04,
                3 => 0x08,
                4 => 0x10,
                5 => 0x20,
                6 => 0x40,
                7 => 0x80,
                _ => 0x00,
            },
        )
    }
    pub fn reset(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        dev.smbus_write_byte_data(0x00, 0x00)
    }
}
