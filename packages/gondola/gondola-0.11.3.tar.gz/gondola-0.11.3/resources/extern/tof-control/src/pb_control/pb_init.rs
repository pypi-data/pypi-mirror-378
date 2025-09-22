use crate::helper::pb_type::PBError;
use crate::pb_control::{pb_temp, pb_vcp};

pub fn initialize() -> Result<(), PBError> {
    // Initialize Temp Sensor
    initialize_temp()?;
    // Initialize VCP Sensor
    initialize_vcp()?;

    Ok(())
}

fn initialize_temp() -> Result<(), PBError> {
    pb_temp::config_temp()?;

    Ok(())
}

fn initialize_vcp() -> Result<(), PBError> {
    pb_vcp::config_vcp()?;

    Ok(())
}