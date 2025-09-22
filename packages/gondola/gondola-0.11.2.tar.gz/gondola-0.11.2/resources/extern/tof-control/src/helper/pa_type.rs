use serde::{Deserialize, Serialize};

/// PA Data Type
// All PA Monitoring Types
#[derive(Debug, Serialize, Deserialize)]
pub struct PAMoniData {
    pub pa_temp: PATemp,
    pub pa_bias: PAReadBias,
}
// PA Temperature Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct PATemp {
    pub pa_temps: [f32; 16],
}
// PA Read SiPM Bias Voltages
#[derive(Debug, Serialize, Deserialize)]
pub struct PAReadBias {
    pub read_biases: [f32; 16],
}
// PA Set SiPM Bias Voltages
#[derive(Debug, Serialize, Deserialize)]
pub struct PASetBias {
    pub set_biases: [f32; 16],
}

/// PA Error Type
#[derive(Debug)]
pub enum PAError {
    // I2C Error
    I2C(i2cdev::linux::LinuxI2CError),
    // PB Error
    PBError(crate::helper::pb_type::PBError),
}

impl std::fmt::Display for PAError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "PAError")
    }
}

impl From<i2cdev::linux::LinuxI2CError> for PAError {
    fn from(e: i2cdev::linux::LinuxI2CError) -> Self {
        PAError::I2C(e)
    }
}

impl From<crate::helper::pb_type::PBError> for PAError {
    fn from(e: crate::helper::pb_type::PBError) -> Self {
        PAError::PBError(e)
    }
}