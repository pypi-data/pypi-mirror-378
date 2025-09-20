#![allow(unused)]
use crate::constant::*;

use i2c_linux_sys::i2c_smbus_read_i2c_block_data;
use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// Register
const INPUT_PORT_0: u16 = 0x00;
const INPUT_PORT_1: u16 = 0x01;
const INPUT_PORT_2: u16 = 0x02;
const INPUT_PORT_3: u16 = 0x03;
const INPUT_PORT_4: u16 = 0x04;
const INPUT_PORT_5: u16 = 0x05;
const INPUT_PORT_6: u16 = 0x06;
const INPUT_PORT_7: u16 = 0x07;
const OUTPUT_PORT_0: u16 = 0x08;
const OUTPUT_PORT_1: u16 = 0x09;
const OUTPUT_PORT_2: u16 = 0x0A;
const OUTPUT_PORT_3: u16 = 0x0B;
const OUTPUT_PORT_4: u16 = 0x0C;
const OUTPUT_PORT_5: u16 = 0x0D;
const OUTPUT_PORT_6: u16 = 0x0E;
const OUTPUT_PORT_7: u16 = 0x0F;
const INTERRUPT_STATUS_PORT_0: u16 = 0x10;
const INTERRUPT_STATUS_PORT_1: u16 = 0x11;
const INTERRUPT_STATUS_PORT_2: u16 = 0x12;
const INTERRUPT_STATUS_PORT_3: u16 = 0x13;
const INTERRUPT_STATUS_PORT_4: u16 = 0x14;
const INTERRUPT_STATUS_PORT_5: u16 = 0x15;
const INTERRUPT_STATUS_PORT_6: u16 = 0x16;
const INTERRUPT_STATUS_PORT_7: u16 = 0x17;
const PORT_SELECT: u16 = 0x18;
const INTERRUPT_MASK: u16 = 0x19;
const PIN_DIRECTION: u16 = 0x1C;
const DRIVE_MODE_PULL_UP: u16 = 0x1D;
const DRIVE_MODE_PULL_DOWN: u16 = 0x1E;
const DRIVE_MODE_OPEN_DRAIN_HIGH: u16 = 0x1F;
const DRIVE_MODE_OPEN_DRAIN_LOW: u16 = 0x20;
const DRIVE_MODE_STRONG: u16 = 0x21;
const DRIVE_MODE_SLOW_STRONG: u16 = 0x22;
const DRIVE_MODE_HIGH_Z: u16 = 0x23;
const ENABLE_REGISTER: u16 = 0x2D;
const DEVICE_INFO: u16 = 0x2E;
const COMMAND: u16 = 0x30;

#[derive(Copy, Clone)]
pub struct CY8C9560A {
    bus: u8,
    address: u16,
}

impl CY8C9560A {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn read_device_info(&self) -> Result<(u8, u8), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let device_info = dev.smbus_read_byte_data(DEVICE_INFO as u8)?;
        let device_family = (device_info & 0xF0) >> 4;
        let device_setting = device_info & 0x01;

        Ok((device_family, device_setting))
    }
    pub fn read_enable_register(&self) -> Result<u8, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let enable_register = dev.smbus_read_byte_data(ENABLE_REGISTER as u8)?;

        Ok(enable_register)
    }
    pub fn enable_eeprom(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let eeprom_enable_sequence: [u8; 4] = [0x43, 0x4D, 0x53, 0x02];
        dev.smbus_write_i2c_block_data(ENABLE_REGISTER as u8, &eeprom_enable_sequence)?;

        Ok(())
    }
    pub fn store_config_eeprom_por(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(COMMAND as u8, 0x01)?;

        Ok(())
    }
    pub fn reset_config_eeprom_por(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(COMMAND as u8, 0x02)?;

        Ok(())
    }
    pub fn read_port_status(&self, port: u8) -> Result<u8, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let port_status = dev.smbus_read_byte_data(match port {
            0 => INPUT_PORT_0 as u8,
            1 => INPUT_PORT_1 as u8,
            2 => INPUT_PORT_2 as u8,
            3 => INPUT_PORT_3 as u8,
            4 => INPUT_PORT_4 as u8,
            5 => INPUT_PORT_5 as u8,
            6 => INPUT_PORT_6 as u8,
            7 => INPUT_PORT_7 as u8,
            _ => 0xFF,
        })?;

        Ok(port_status)
    }
    pub fn initialize_all_outputs(&self) -> Result<(), LinuxI2CError> {
        for i in 0..8 {
            self.set_output_port(i, 0xFF)?;
        }

        Ok(())
    }
    pub fn set_output_port(&self, port: u8, value: u8) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(
            match port {
                0 => OUTPUT_PORT_0 as u8,
                1 => OUTPUT_PORT_1 as u8,
                2 => OUTPUT_PORT_2 as u8,
                3 => OUTPUT_PORT_3 as u8,
                4 => OUTPUT_PORT_4 as u8,
                5 => OUTPUT_PORT_5 as u8,
                6 => OUTPUT_PORT_6 as u8,
                7 => OUTPUT_PORT_7 as u8,
                _ => 0xFF,
            },
            value,
        )?;

        Ok(())
    }
    pub fn select_port(&self, port: u8) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(PORT_SELECT as u8, port)?;

        Ok(())
    }
    pub fn set_interrupt_mask_port(&self, value: u8) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(INTERRUPT_MASK as u8, value)?;

        Ok(())
    }
    pub fn set_pin_direction(&self, value: u8) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(PIN_DIRECTION as u8, value)?;

        Ok(())
    }
    pub fn set_drive_mode(&self, mode: u8) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(
            match mode {
                0 => DRIVE_MODE_PULL_UP as u8,
                1 => DRIVE_MODE_PULL_DOWN as u8,
                2 => DRIVE_MODE_OPEN_DRAIN_HIGH as u8,
                3 => DRIVE_MODE_OPEN_DRAIN_LOW as u8,
                4 => DRIVE_MODE_STRONG as u8,
                5 => DRIVE_MODE_SLOW_STRONG as u8,
                6 => DRIVE_MODE_HIGH_Z as u8,
                _ => 0xFF,
            },
            0x01,
        )?;

        Ok(())
    }
    // Set RF Switch (HMC849)
    pub fn set_rf_switch(&self, channel: u8, mode: u8) -> Result<(), LinuxI2CError> {
        match channel {
            0 => match mode {
                0 => {
                    let value: u8 = (0x3F & !0x30) | 0x20;
                    self.set_output_port(7, value)?;
                }
                1 => {
                    let value: u8 = (0x3F & !0x30) | 0x10;
                    self.set_output_port(7, value)?;
                }
                2 => {
                    let value: u8 = (0x3F & !0x30) | 0x00;
                    self.set_output_port(7, value)?;
                }
                _ => {
                    self.set_output_port(7, 0x3F)?;
                }
            },
            1 => match mode {
                0 => {
                    let value: u8 = (0x3F | 0x0C) & 0x0C;
                    self.set_output_port(7, value)?;
                }
                1 => {
                    let value: u8 = (0x3F & !0x0C) | 0x04;
                    self.set_output_port(7, value)?;
                }
                2 => {
                    let value: u8 = (0x3F & !0x0C) | 0x00;
                    self.set_output_port(7, value)?;
                }
                _ => {
                    self.set_output_port(7, 0x3F)?;
                }
            },
            2 => match mode {
                0 => {
                    let value: u8 = (0x3F | 0x03) & 0x03;
                    self.set_output_port(7, value)?;
                }
                1 => {
                    let value: u8 = (0x3F & !0x03) | 0x01;
                    self.set_output_port(7, value)?;
                }
                2 => {
                    let value: u8 = (0x3F & !0x03) | 0x00;
                    self.set_output_port(7, value)?;
                }
                _ => {
                    self.set_output_port(7, 0x3F)?;
                }
            },
            3 => match mode {
                0 => {
                    let value: u8 = (0x03 | 0x03) & 0x03;
                    self.set_output_port(2, value)?;
                }
                1 => {
                    let value: u8 = (0x03 & !0x03) | 0x01;
                    self.set_output_port(2, value)?;
                }
                2 => {
                    let value: u8 = (0x03 & !0x03) | 0x00;
                    self.set_output_port(2, value)?;
                }
                _ => {
                    self.set_output_port(2, 0x03)?;
                }
            },
            4 => match mode {
                0 => {
                    let value: u8 = (0x33 | 0x03) & 0x03;
                    self.set_output_port(5, value)?;
                }
                1 => {
                    let value: u8 = (0x33 & !0x03) | 0x02;
                    self.set_output_port(5, value)?;
                }
                2 => {
                    let value: u8 = (0x33 & !0x03) | 0x00;
                    self.set_output_port(5, value)?;
                }
                _ => {
                    self.set_output_port(5, 0x33)?;
                }
            },
            5 => match mode {
                0 => {
                    let value: u8 = (0x33 | 0x30) & 0x30;
                    self.set_output_port(5, value)?;
                }
                1 => {
                    let value: u8 = (0x33 & !0x30) | 0x10;
                    self.set_output_port(5, value)?;
                }
                2 => {
                    let value: u8 = (0x33 & !0x30) | 0x00;
                    self.set_output_port(5, value)?;
                }
                _ => {
                    self.set_output_port(5, 0x33)?;
                }
            },
            6 => match mode {
                0 => {
                    let value: u8 = (0xFC | 0xC0) & 0xC0;
                    self.set_output_port(4, value)?;
                }
                1 => {
                    let value: u8 = (0xFC & !0xC0) | 0x80;
                    self.set_output_port(4, value)?;
                }
                2 => {
                    let value: u8 = (0xFC & !0xC0) | 0x00;
                    self.set_output_port(4, value)?;
                }
                _ => {
                    self.set_output_port(4, 0xFC)?;
                }
            },
            7 => match mode {
                0 => {
                    let value: u8 = (0xFC | 0x30) & 0x30;
                    self.set_output_port(4, value)?;
                }
                1 => {
                    let value: u8 = (0xFC & !0x30) | 0x20;
                    self.set_output_port(4, value)?;
                }
                2 => {
                    let value: u8 = (0xFC & !0x30) | 0x00;
                    self.set_output_port(4, value)?;
                }
                _ => {
                    self.set_output_port(4, 0xFC)?;
                }
            },
            8 => match mode {
                0 => {
                    let value: u8 = (0xFC | 0x0C) & 0x0C;
                    self.set_output_port(4, value)?;
                }
                1 => {
                    let value: u8 = (0xFC & !0x0C) | 0x08;
                    self.set_output_port(4, value)?;
                }
                2 => {
                    let value: u8 = (0xFC & !0x0C) | 0x00;
                    self.set_output_port(4, value)?;
                }
                _ => {
                    self.set_output_port(4, 0xFC)?;
                }
            },
            _ => {}
        };

        Ok(())
    }
    // neet to check!
    pub fn reset_clock_synthesizer(&self) -> Result<(), LinuxI2CError> {
        let mut value = (0x03 & !0x02) | 0 << 1;
        value = (value & !0x01) | 1;

        self.set_output_port(3, value)?;

        Ok(())
    }
    // neet to check!
    pub fn enable_tcal_clock(&self) -> Result<(), LinuxI2CError> {
        let mut value: u16 = (0x3F | 0x80) | (0x01 << 8);
        self.set_output_port(7, value as u8)?;

        value = (0x3F | 0x40) | (0x01 << 7);
        self.set_output_port(7, value as u8)?;

        Ok(())
    }
    pub fn disable_tcal_clock(&self) -> Result<(), LinuxI2CError> {
        let mut value: u16 = (0x3F | 0x80);
        self.set_output_port(7, value as u8)?;

        value = (0x3F | 0x40);
        self.set_output_port(7, value as u8)?;

        Ok(())
    }
}
