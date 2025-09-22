use crate::constant::*;
use crate::helper::rb_type::{RBMag, RBError};
use crate::device::{lis3mdltr, pca9548a};

impl RBMag {
    pub fn new() -> Self {
        match Self::read_mag() {
            Ok(rb_mag) => {
                rb_mag
            }
            Err(_) => {
                Self {
                    mag_xyz: [f32::MAX; 3],
                }
            }
        }
    }
    pub fn read_mag() -> Result<RBMag, RBError> {
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
        i2c_mux.select(RB_LIS3MDLTR_CHANNEL)?;

        let lis3mdltr = lis3mdltr::LIS3MDLTR::new(I2C_BUS, RB_LIS3MDLTR_ADDRESS);
        lis3mdltr.configure()?;
        let mag_xyz = lis3mdltr.read_mag()?;

        i2c_mux.reset()?;

        Ok(
            RBMag {
                mag_xyz,
            }
        )
    }
}

pub fn config_mag() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
    i2c_mux.select(RB_LIS3MDLTR_CHANNEL)?;
    let lis3mdltr = lis3mdltr::LIS3MDLTR::new(I2C_BUS, RB_LIS3MDLTR_ADDRESS);
    lis3mdltr.configure()?;

    i2c_mux.reset()?;

    Ok(())
}