use i2cdev::core::*;
use i2cdev::linux::LinuxI2CDevice;

use crate::constant::*;
use crate::helper::ltb_type::{LTBTemp, LTBError};
use crate::device::tmp112;

impl LTBTemp {
    pub fn new() -> Self {
        match Self::read_temp() {
            Ok(ltb_temp) => {
                ltb_temp
            }
            Err(_) => {
                Self {
                    trenz_temp: f32::MAX,
                    board_temp: f32::MAX,
                }
            }
        }
    }
    pub fn read_temp() -> Result<LTBTemp, LTBError> {
        let trenz_temp = Self::trenz_temp()?;
        let board_temp = Self::board_temp()?;

        Ok(
            LTBTemp {
                trenz_temp,
                board_temp,
            }
        )
    }
    pub fn board_temp() -> Result<f32, LTBError> {
        let board_tmp112 = tmp112::TMP112::new(I2C_BUS, LTB_TMP112_ADDRESS);
        board_tmp112.config()?;
        let board_temp = board_tmp112.read()?;

        Ok(board_temp)
    }
    pub fn trenz_temp() -> Result<f32, LTBError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", I2C_BUS), LTB_TRENZ_ADDRESS)?;
        let trenz_temp_raw = dev.smbus_read_i2c_block_data(LTB_TRENZ_TEMP_OFFSET as u8, 2)?;
        let trenz_temp_adc =
            (((trenz_temp_raw[0] as u16) << 4) | ((trenz_temp_raw[1] as u16) >> 4)) & 0xFFF;
        let trenz_temp = (((trenz_temp_adc & 4095) as f32 * 503.975) / 4096.0) - 273.15;

        Ok(trenz_temp)
    }
}

pub fn config_temp() -> Result<(), LTBError> {
    let ltb_tmp112 = tmp112::TMP112::new(I2C_BUS, LTB_TMP112_ADDRESS);
    ltb_tmp112.config()?;

    Ok(())
}