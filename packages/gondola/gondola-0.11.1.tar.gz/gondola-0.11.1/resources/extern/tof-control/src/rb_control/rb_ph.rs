use crate::constant::*;
use crate::helper::rb_type::{RBPh, RBError};
use crate::device::{bme280, pca9548a};

impl RBPh {
    pub fn new() -> Self {
        match Self::read_ph() {
            Ok(rb_ph) => {
                rb_ph
            }
            Err(_) => {
                Self {
                    pressure: f32::MAX,
                    humidity: f32::MAX,
                }
            }
        }
    }
    pub fn read_ph() -> Result<RBPh, RBError> {
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);

        i2c_mux.select(RB_BME280_CHANNEL)?;
        let bme280 = bme280::BME280::new(I2C_BUS, RB_BME280_ADDRESS);
        bme280.configure()?;
        let ph = bme280.read()?;
        let pressure = ph[0];
        let humidity = ph[1];

        i2c_mux.reset()?;

        Ok(
            RBPh {
                pressure,
                humidity,
            }
        )
    }
}

pub fn config_ph() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
    i2c_mux.select(RB_BME280_CHANNEL)?;
    let bme280 = bme280::BME280::new(I2C_BUS, RB_BME280_ADDRESS);
    bme280.configure()?;

    i2c_mux.reset()?;

    Ok(())
}