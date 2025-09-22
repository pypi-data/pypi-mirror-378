#![allow(unused)]
use libc::{ioctl, O_RDWR, STDOUT_FILENO};
use std::fs::File;
use std::os::fd::{AsRawFd, IntoRawFd, RawFd};
use std::os::raw::{c_uint, c_ulong};

use crate::constant::*;

use i2c_linux_sys::*;

const READBACK_ENABLE: u16 = 0x90;
const POWER_DOWN_UP: u16 = 0x40;

pub struct AD5675 {
    fd: RawFd,
    address: u16,
}
impl AD5675 {
    pub fn new(address: u16) -> Self {
        let fd = if let Ok(file) = File::open("/dev/i2c-0") {
            file.into_raw_fd()
        } else {
            STDOUT_FILENO
        };
        Self { fd, address }
    }
    pub fn write_dac(&self, channel: u8, value: u16) {
        unsafe { ioctl(self.fd, (I2C_SLAVE as c_ulong).try_into().unwrap(), 0x77) };
        i2c_linux_sys::i2c_smbus_write_byte(self.fd, 0x04);
        unsafe {
            ioctl(
                self.fd,
                (I2C_SLAVE as c_ulong).try_into().unwrap(),
                self.address as c_uint,
            )
        };
        let mut buffer = (value & 0xFF00) >> 8;
        buffer = buffer | (value & 0x00FF) << 8;
        i2c_linux_sys::i2c_smbus_write_word_data(self.fd, 0x30 + channel, buffer);
    }
    // pub fn read_dac(&self, channel: u8) {
    //     i2c_linux_sys::i2c_set_slave_address(self.fd, self.address, false);
    //     // i2c_linux_sys::i2c_smbus_write_byte(self.fd, READBACK_ENABLE as u8);
    //     // let mut buffer: [u8; 2] = [0, 0];
    //     let mut reg: u8 = 0x10|channel;
    //     // i2c_linux_sys::i2c_smbus_read_i2c_block_data(self.fd, channel, &mut buffer);
    //     // i2c_linux_sys::i2c_smbus_read_i2c_block_data(self.fd, 0x30+channel, &mut buffer);
    //     let mut i2c_msg_custom = i2c_linux_sys::i2c_msg {
    //         addr: self.address,
    //         flags: i2c_linux_sys::Flags::RD,
    //         len: 2,
    //         buf: &mut reg,
    //     };
    //     let mut i2c_rdwr_ioctl_data_custom = i2c_linux_sys::i2c_rdwr_ioctl_data {
    //         msgs: &mut i2c_msg_custom,
    //         nmsgs: 2,
    //     };
    //     let data = unsafe { i2c_linux_sys::ioctls::i2c_rdwr(self.fd, &mut i2c_rdwr_ioctl_data_custom) };
    //     println!("{:?}", data);
    // }
}
