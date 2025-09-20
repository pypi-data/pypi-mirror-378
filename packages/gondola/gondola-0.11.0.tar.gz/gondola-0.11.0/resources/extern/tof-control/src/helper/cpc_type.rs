#[derive(Debug)]
pub struct CPCTemp {
    pub cpc_temp: f32,
}

#[derive(Debug)]
pub enum CPCTempError {
    /// I2C Error
    I2C(i2cdev::linux::LinuxI2CError),
}

impl From<i2cdev::linux::LinuxI2CError> for CPCTempError {
    fn from(e: i2cdev::linux::LinuxI2CError) -> Self {
        CPCTempError::I2C(e)
    }
}