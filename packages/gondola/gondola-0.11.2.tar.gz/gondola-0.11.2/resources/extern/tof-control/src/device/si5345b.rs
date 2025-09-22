#![allow(unused)]
use crate::constant::*;

use csv;
use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};
use std::thread;
use std::time::Duration;

const SET_PAGE: u16 = 0x01;

const LOL_HOLD_STATUS: u16 = 0x00E;
const SOFT_RST_ALL: u16 = 0x001C; // Bits: 0
const HARD_RST: u16 = 0x001E; // Bits: 1
                              // Registers for NVM Programming
const ACTIVE_NVM_BANK: u16 = 0x00E2; // [7:0], R, Indicates number of user bank writes carried out so far.A
const NVM_WRITE: u16 = 0x00E3; // [7:0], R/W, Initiates an NVM write when written with 0xC7
const NVM_READ_BANK: u16 = 0x00E4; // [0], S, Download register values with content stored in NVM
const DEVICE_READY: u16 = 0x00FE; // [7:0], R, Indicates that the device serial interface is ready to accept commands.

pub struct SI5345B {
    bus: u8,
    address: u16,
}

impl SI5345B {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }

    pub fn read_lol_status(&self) -> Result<(bool), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(SET_PAGE as u8, ((LOL_HOLD_STATUS >> 8) as u8));

        let mut lol_status = dev.smbus_read_byte_data(LOL_HOLD_STATUS as u8)?;
        lol_status = lol_status & 0x02;

        if lol_status == 1 {
            Ok(true)
        } else {
            Ok(false)
        }
    }

    pub fn read_holdover_status(&self) -> Result<(bool), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(SET_PAGE as u8, ((LOL_HOLD_STATUS >> 8) as u8));

        let mut dspll_mode = dev.smbus_read_byte_data(LOL_HOLD_STATUS as u8)?;
        dspll_mode = dspll_mode & 0x20;

        if dspll_mode == 1 {
            Ok(true)
        } else {
            Ok(false)
        }
    }

    pub fn configure_si5345b(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        let si5345b_csv = include_str!("../config/rb_config/si5345b.csv");
        let mut reader = csv::ReaderBuilder::new()
            .comment(Some(b'#'))
            .escape(Some(b'\\'))
            .flexible(true)
            .from_reader(si5345b_csv.as_bytes());

        for (i, record) in reader.records().enumerate() {
            let record = record.expect("failed to convert record");
            let address = i64::from_str_radix(&record[0].trim_start_matches("0x"), 16)
                .expect("cannot convert register from address");
            let data = i64::from_str_radix(&record[1].trim_start_matches("0x"), 16)
                .expect("cannot convert register from data");
            let page = address >> 8;
            let register = address & 0xFF;
            // println!("{} {:?} {:?}", i, address, data);

            dev.smbus_write_byte_data(SET_PAGE as u8, page as u8);
            dev.smbus_write_byte_data(register as u8, data as u8);

            if i == 2 {
                thread::sleep(Duration::from_millis(300));
            }
        }

        Ok(())
    }

    /// Check how many user bank writes has carried out so far
    pub fn read_available_nvm_bank(&self) -> Result<u8, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        let active_nvm_bank_page = ACTIVE_NVM_BANK >> 8;
        let active_nvm_bank_reg = ACTIVE_NVM_BANK & 0xFF;
        dev.smbus_write_byte_data(SET_PAGE as u8, active_nvm_bank_page as u8);
        let active_nvm_bank = dev.smbus_read_byte_data(active_nvm_bank_reg as u8)?;
        
        let mut num_available_bank: u8;
        match active_nvm_bank {
            3 => num_available_bank = 2,
            15 => num_available_bank = 1,
            63 => num_available_bank = 0,
            _ => num_available_bank = u8::MAX,
        }

        Ok((num_available_bank))
    }

    pub fn configure_nvm_si5345b(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        // /// Write all registers as needed
        // self.configure_si5345b()?;
        // thread::sleep(Duration::from_millis(300));

        /// Write identification into the user scratch space (registers 0x026B to 0x0272)
        let design_id = String::from("RB2.5.2");
        let mut design_id_ary: [u8; 8] = [0; 8];
        for (i, char) in design_id.clone().into_bytes().iter().enumerate() {
            design_id_ary[i] = *char;
        }
        let mut scratch_space_reg: u16 = 0x026B;
        // println!("Writing identification into the user scratch space (registers 0x026B to 0x0272)...");
        for byte in design_id_ary.iter() {
            let page = scratch_space_reg >> 8;
            let register = scratch_space_reg & 0xFF;
            dev.smbus_write_byte_data(SET_PAGE as u8, page as u8);
            dev.smbus_write_byte_data(register as u8, *byte);

            scratch_space_reg += 1;
        }

        /// Write 0xC7 to NVM_WRITE (0x00E3) register
        let nvm_write_page = NVM_WRITE >> 8;
        let nvm_write_reg = NVM_WRITE & 0xFF;
        // println!("Writing 0xC7 to NVM_WRITE (0x00E3) register...");
        dev.smbus_write_byte_data(SET_PAGE as u8, nvm_write_page as u8);
        dev.smbus_write_byte_data(nvm_write_reg as u8, 0xC7);
        thread::sleep(Duration::from_millis(300));

        /// Wait until DEVICE_READY (0x00FE) = 0x0F
        let device_ready_page = DEVICE_READY >> 8;
        let device_ready_reg = DEVICE_READY & 0xFF;
        dev.smbus_write_byte_data(SET_PAGE as u8, device_ready_page as u8);
        let mut device_ready_data = dev.smbus_read_byte_data(device_ready_reg as u8)?;
        while device_ready_data != 0x0F {
            thread::sleep(Duration::from_millis(300));
            dev.smbus_write_byte_data(SET_PAGE as u8, device_ready_page as u8);
            device_ready_data = dev.smbus_read_byte_data(device_ready_reg as u8)?;
        }

        /// Set NVM_READ_BANK (0x00E4[0]) = “1”
        let nvm_read_bank_page = NVM_READ_BANK >> 8;
        let nvm_read_bank_reg = NVM_READ_BANK & 0xFF;
        // println!("Writing 1 to NVM_READ_BANK (0x00E4[0]) register...");
        dev.smbus_write_byte_data(SET_PAGE as u8, nvm_read_bank_page as u8);
        dev.smbus_write_byte_data(nvm_read_bank_reg as u8, 0x01);
        thread::sleep(Duration::from_millis(300));

        /// Wait until DEVICE_READY (0x00FE) = 0x0F
        dev.smbus_write_byte_data(SET_PAGE as u8, device_ready_page as u8);
        device_ready_data = dev.smbus_read_byte_data(device_ready_reg as u8)?;
        while device_ready_data != 0x0F {
            thread::sleep(Duration::from_millis(300));
            dev.smbus_write_byte_data(SET_PAGE as u8, device_ready_page as u8);
            device_ready_data = dev.smbus_read_byte_data(device_ready_reg as u8)?;
        }

        Ok(())
    }

    pub fn hard_reset_si5345b(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(SET_PAGE as u8, ((HARD_RST >> 8) as u8));

        let mut value = dev.smbus_read_byte_data((HARD_RST & 0xFF) as u8)?;
        value = value | 0x02;
        dev.smbus_write_byte_data((HARD_RST & 0xFF) as u8, value);

        value = value & 0xFD;
        dev.smbus_write_byte_data((HARD_RST & 0xFF) as u8, value);

        Ok(())
    }

    pub fn soft_reset_si5345b(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_byte_data(SET_PAGE as u8, ((SOFT_RST_ALL >> 8) as u8));

        dev.smbus_write_byte_data((SOFT_RST_ALL & 0xFF) as u8, 0x01);

        Ok(())
    }
}
