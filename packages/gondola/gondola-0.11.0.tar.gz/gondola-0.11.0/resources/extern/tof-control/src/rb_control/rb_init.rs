use gethostname::gethostname;

use crate::constant::*;
use crate::helper::rb_type::RBError;
use crate::memory::{read_control_reg, write_control_reg};
use crate::rb_control::{rb_temp, rb_vcp, rb_ph, rb_mag, rb_dac};

pub fn initialize() -> Result<(), RBError> {    
    // Initialize DAC Chip
    initialize_dac()?;
    // Set RB ID
    set_board_id()?;
    // Initialize DAQ Registers
    initialize_daq()?;
    // Initialize I2C Sensors
    initialize_sensor()?;

    Ok(())
}

fn initialize_dac() -> Result<(), RBError> {
    rb_dac::set_dac()?;

    Ok(())
}

fn set_board_id() -> Result<(), RBError> {
    let hostname = gethostname().into_string()?;
    let board_id = hostname.replace("tof-rb", "").parse::<u32>()?;

    write_control_reg(BOARD_ID, board_id)?;

    Ok(())
}

fn initialize_daq() -> Result<(), RBError> {
    // Disable DAQ Fragment
    disable_daq_fragment()?;

    // Enable Spike Clean
    enable_spike_clean()?;

    // Enable 1-8 Channels
    enable_8_channels()?;

    // Enable 9th Channel
    enable_9th_channel()?;

    // Start DRS Chip
    start_drs()?;

    Ok(())
}

fn disable_daq_fragment() -> Result<(), RBError> {
    let value = read_control_reg(DAQ_FRAGMENT_EN)?;
    if (value & 0x01) == 0x01 {
        write_control_reg(DAQ_FRAGMENT_EN, 0x00)?;
    }

    Ok(())
} 

fn enable_spike_clean() -> Result<(), RBError> {
    let mut value = read_control_reg(EN_SPIKE_REMOVAL)?;
    value = value | 0x400000;
    if ((value >> 22) & 0x01) != 0x01 {
        write_control_reg(EN_SPIKE_REMOVAL, value)?;
    }

    Ok(())
}

fn enable_8_channels() -> Result<(), RBError> {
    let mut value = read_control_reg(READOUT_MASK)?;
    value = value | 0x1FF;
    if (value & 0x1FF) != 0x1FF {
        write_control_reg(READOUT_MASK, value)?;
    }

    Ok(())
}

fn enable_9th_channel() -> Result<(), RBError> {
    let mut value = read_control_reg(READOUT_MASK)?;
    value = value | 0x3FF;
    if ((value >> 9) & 0x01) != 0x01 {
        write_control_reg(READOUT_MASK, value)?;
    }

    Ok(())
}

fn start_drs() -> Result<(), RBError> {
    write_control_reg(START, 0x01)?;

    Ok(())
}

fn initialize_sensor() -> Result<(), RBError> {
    // Configure Temp Sensors (TMP112)
    rb_temp::config_temp()?;
    // Configure VCP Sensors (INA226 and INA200)
    rb_vcp::config_vcp()?;
    // Configure PH Sensor (BME280)
    rb_ph::config_ph()?;
    // Configure Magnetic Sensor (LIS3MDLTR)
    rb_mag::config_mag()?;

    Ok(())
}
