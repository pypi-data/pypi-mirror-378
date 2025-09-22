use std::thread;
use std::time::Duration;

use crate::constant::*;
use crate::memory::{read_control_reg, write_control_reg};
use crate::helper::rb_type::RBError;
use crate::rb_control::{rb_temp, rb_vcp, rb_ph, rb_mag, rb_dac, rb_gpioe, rb_clk};

pub fn reset() -> Result<(), RBError> {
    reset_gpioe()?;
    reset_clk_synth()?;
    reset_dac()?;

    thread::sleep(Duration::from_millis(500));
    reset_daq()?;

    reset_sensor()?;

    Ok(())
}

fn reset_gpioe() -> Result<(), RBError> {
    rb_gpioe::reset_gpioe()?;
    rb_gpioe::initialize_gpioe()?;
    rb_gpioe::rf_input_select_gpioe(2)?;
    rb_gpioe::enable_si5345b_gpioe()?;

    Ok(())
}

fn reset_clk_synth() -> Result<(), RBError> {
    rb_clk::reset_clk_synth(0)?;

    Ok(())
}

fn reset_dac() -> Result<(), RBError> {
    rb_dac::set_dac()?;

    Ok(())
}

fn reset_daq() -> Result<(), RBError> {
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

fn reset_sensor() -> Result<(), RBError> {
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