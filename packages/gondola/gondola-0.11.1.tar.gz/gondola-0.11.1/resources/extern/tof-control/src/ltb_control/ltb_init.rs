use crate::ltb_control::{ltb_temp, ltb_threshold};
use crate::helper::ltb_type::LTBError;

pub fn initialize() -> Result<(), LTBError> {
    // Set Default Threshold Voltages
    initialize_threshold()?;
    // Initialize Temp Sensor
    initialize_temp()?;
    
    Ok(())
}

fn initialize_threshold() -> Result<(), LTBError> {
    ltb_threshold::set_default_threshold()?;

    Ok(())
}

fn initialize_temp() -> Result<(), LTBError> {
    // Configure Temp Sensors (TMP112)
    ltb_temp::config_temp()?;

    Ok(())
}