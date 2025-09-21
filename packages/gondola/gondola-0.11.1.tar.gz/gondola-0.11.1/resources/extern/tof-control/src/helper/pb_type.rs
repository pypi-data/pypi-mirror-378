use serde::{Deserialize, Serialize};

/// PB Data Type
// All PB Monitoring Types
#[derive(Debug, Serialize, Deserialize)]
pub struct PBMoniData {
    pub pb_temp: PBTemp,
    pub pb_vcp: PBVcp,
}
// PB Temperature Sensor Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct PBTemp {
    pub pds_temp: f32,
    pub pas_temp: f32,
    pub nas_temp: f32,
    pub shv_temp: f32,
}
// PB VCP (Voltage, Current and Power) Sensor
#[derive(Debug, Serialize, Deserialize)]
pub struct PBVcp {
    pub p3v6_pa_vcp:    [f32; 3],
    pub n1v6_pa_vcp:    [f32; 3],
    pub p3v4f_ltb_vcp:      [f32; 3],
    pub p3v4d_ltb_vcp:      [f32; 3],
    pub p3v6_ltb_vcp:       [f32; 3],
    pub n1v6_ltb_vcp:       [f32; 3],
}

/// PB Error Type
#[derive(Debug)]
pub enum PBError {
    // I2C Error
    I2C(i2cdev::linux::LinuxI2CError),
}

impl std::fmt::Display for PBError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "PBError")
    }
}

impl From<i2cdev::linux::LinuxI2CError> for PBError {
    fn from(e: i2cdev::linux::LinuxI2CError) -> Self {
        PBError::I2C(e)
    }
}