use crate::constant::*;
use crate::helper::pb_type::PBError;
use crate::device::{max7320, pca9548a};

pub fn ltb_pwr_switch(switch: bool) -> Result<(), PBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
    i2c_mux.select(PB_MAX7320_CHANNEL)?;

    let ltb_pwr = max7320::MAX7320::new(I2C_BUS, PB_MAX7320_ADDRESS);
    if switch {
        ltb_pwr.output_on_0_3()?;
    } else {
        ltb_pwr.output_off_all()?;
    }

    i2c_mux.reset()?;

    Ok(())
}