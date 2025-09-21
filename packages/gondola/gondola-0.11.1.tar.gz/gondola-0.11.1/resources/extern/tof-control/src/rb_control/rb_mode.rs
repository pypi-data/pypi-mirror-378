use crate::helper::rb_type::RBError;
use crate::rb_control::{rb_dac, rb_input, rb_gpioe};

pub fn select_noi_mode() -> Result<(), RBError> {
    rb_dac::dac_noi_mode()?;
    rb_input::disable_rf_input()?;

    Ok(())
}

pub fn select_vcal_mode() -> Result<(), RBError> {
    rb_dac::dac_vcal_mode()?;
    rb_input::disable_rf_input()?;

    Ok(())
}

pub fn select_tcal_mode() -> Result<(), RBError> {
    rb_dac::dac_tcal_mode()?;
    rb_input::enable_tca_input()?;

    Ok(())
}

pub fn select_sma_mode() -> Result<(), RBError> {
    rb_dac::dac_sma_mode()?;
    rb_input::enable_sma_input()?;

    Ok(())
}

pub fn read_input_mode() -> Result<String, RBError> {
    
    let mut rf_input_ports: [u8; 9] = Default::default();
    for i in 0..9 {
        let rf_input_port = rb_gpioe::read_rf_input_port(i+1 as u8)?;
        rf_input_ports[i as usize] = rf_input_port;
    }

    let input_mode: &str;
    match rf_input_ports {
        [0, 0, 0, 0, 0, 0, 0, 0, 0] => {
            input_mode = "SMA";
        }
        [1, 1, 1, 1, 1, 1, 1, 1, 1] => {
            input_mode = "TCAL";
        }
        [3, 3, 3, 3, 3, 3, 3, 3, 3] => {
            input_mode = "NOI";
        }
        _ => {
            input_mode = "Input Mode Error";
        }
    }

    Ok(input_mode.to_string())
}
