#[derive(Debug)]
pub struct TCPCTemp {
    pub tcpc_temp: f32,
}

#[derive(Debug)]
pub struct TCPCVcp {
    pub tcpc_vcp: [f32; 3],
}

#[derive(Debug)]
pub enum TCPCTempError {
    /// I2C Error
    I2C(i2cdev::linux::LinuxI2CError),
}

impl From<i2cdev::linux::LinuxI2CError> for TCPCTempError {
    fn from(e: i2cdev::linux::LinuxI2CError) -> Self {
        TCPCTempError::I2C(e)
    }
}

#[derive(Debug)]
pub enum TCPCVcpError {
    /// I2C Error
    I2C(i2cdev::linux::LinuxI2CError),
}

impl From<i2cdev::linux::LinuxI2CError> for TCPCVcpError {
    fn from(e: i2cdev::linux::LinuxI2CError) -> Self {
        TCPCVcpError::I2C(e)
    }
}