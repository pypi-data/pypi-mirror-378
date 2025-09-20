use serde::{Deserialize, Serialize};

/// LTB Data Type
// All LTB Monitoring Types
#[derive(Debug, Serialize, Deserialize)]
pub struct LTBMoniData {
    pub ltb_temp: LTBTemp,
    pub ltb_thresh: LTBThreshold,
}
// LTB Temperature Sensor Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct LTBTemp {
    pub trenz_temp: f32,
    pub board_temp: f32,
}
// LTB Threshold Voltage Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct LTBThreshold {
    pub thresh_0: f32,
    pub thresh_1: f32,
    pub thresh_2: f32,
}

/// LTB Error Type
#[derive(Debug)]
pub enum LTBError {
    // I2C Error
    I2C(i2cdev::linux::LinuxI2CError),
    // Setting Threshold Error
    SetThreshold,
}

impl std::fmt::Display for LTBError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "LTBError")
    }
}

impl From<i2cdev::linux::LinuxI2CError> for LTBError {
    fn from(e: i2cdev::linux::LinuxI2CError) -> Self {
        LTBError::I2C(e)
    }
}