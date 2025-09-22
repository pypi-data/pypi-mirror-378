use serde::{Deserialize, Serialize};

/// RB Data Type
// All RB Monitoring Types
#[derive(Debug, Serialize, Deserialize)]
pub struct RBMoniData {
    pub rb_info: RBInfo,
    pub rb_temp: RBTemp,
    pub rb_vcp: RBVcp,
    pub rb_ph: RBPh,
    pub rb_mag: RBMag,
}
// RB Information Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct RBInfo {
    pub board_id        : u8,
    pub sub_board       : u8,
    pub lol             : u8,
    pub lol_stable      : u8,
    pub trig_rate       : u16,
    pub fw_version      : String,
    pub fw_hash         : String,
    pub uptime          : u32,
    pub sd_usage        : u8,
    pub input_mode      : String,
    pub rat_num         : u8,
    pub rat_pos         : u8,
    pub rb_pos          : u8, 
}
// RB Temperature Sensor Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct RBTemp {
    pub zynq_temp       : f32,
    pub drs_temp        : f32,
    pub clk_temp        : f32,
    pub adc_temp        : f32,
    pub bme280_temp     : f32,
    pub lis3mdltr_temp  : f32,
}
// RB VCP (Voltage, Current and Power) Sensor Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct RBVcp {
    pub zynq_vcp        : [f32; 3],
    pub p3v3_vcp        : [f32; 3],
    pub p3v5_vcp        : [f32; 3],
    pub n1v5_vcp        : [f32; 3],
    pub drs_dvdd_vcp    : [f32; 3],
    pub drs_avdd_vcp    : [f32; 3],
    pub adc_dvdd_vcp    : [f32; 3],
    pub adc_avdd_vcp    : [f32; 3],
}
// RB HP (Humidity and Pressure) Sensor Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct RBPh {
    pub pressure        : f32,
    pub humidity        : f32,
}
// RB Magnetic Sensor Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct RBMag {
    pub mag_xyz         : [f32; 3],
}

/// RB Error Type
#[derive(Debug)]
pub enum RBError {
    // Register Error
    Register(crate::memory::RegisterError),
    // I2C Error
    I2C(i2cdev::linux::LinuxI2CError),
    // JSON Error
    JSON(serde_json::Error),
    // ParseInt Error
    ParseInt(std::num::ParseIntError),
    // OsString Error
    OsString,
}

impl std::fmt::Display for RBError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "RBError")
    }
}

impl From<crate::memory::RegisterError> for RBError {
    fn from(e: crate::memory::RegisterError) -> Self {
        RBError::Register(e)
    }
}

impl From<i2cdev::linux::LinuxI2CError> for RBError {
    fn from(e: i2cdev::linux::LinuxI2CError) -> Self {
        RBError::I2C(e)
    }
}

impl From<serde_json::Error> for RBError {
    fn from(e: serde_json::Error) -> Self {
        RBError::JSON(e)
    }
}

impl From<std::num::ParseIntError> for RBError {
    fn from(e: std::num::ParseIntError) -> Self {
        RBError::ParseInt(e)
    }
}

impl From<std::ffi::OsString> for RBError {
    fn from(_: std::ffi::OsString) -> Self {
        RBError::OsString
    }
}