pub mod switch_info;
pub mod switch_port;
pub mod switch_util;

use crate::constant::*;
use crate::helper::switch_type::{AllSwitchData, SwitchData, SwitchInfo, SwitchPort, SwitchError};

use switch_util::print_switch_data;
use switch_port::clear_port_statistics;

impl AllSwitchData {
    pub fn new() -> Self {
        match Self::get_all_switch_data() {
            Ok(all_switch_data) => {
                all_switch_data
            }
            Err(_) => {
                Self {
                    switch1: None,
                    switch2: None,
                    switch3: None,
                }
            }
        }
    }
    pub fn get_all_switch_data() -> Result<AllSwitchData, SwitchError> {
        let switch1_data = Self::get_switch_data(1)?;
        let switch2_data = Self::get_switch_data(2)?;
        let switch3_data = Self::get_switch_data(3)?;

        Ok(
            AllSwitchData {
                switch1: Some(switch1_data),
                switch2: Some(switch2_data),
                switch3: Some(switch3_data),
            }
        )
    }
    pub fn get_switch_data(switch: u8) -> Result<SwitchData, SwitchError> {
        let switch_addr: &str;
        match switch {
            1 => switch_addr = SWITCH1_ADDRESS,
            2 => switch_addr = SWITCH2_ADDRESS,
            3 => switch_addr = SWITCH3_ADDRESS,
            4 => switch_addr = SWITCH4_ADDRESS,
            _ => return Err(SwitchError::Address),
        }
        let switch1_info = SwitchInfo::read_info(switch_addr)?;
        let switch1_port = SwitchPort::read_port(switch_addr)?;
        
        Ok(
            SwitchData {
                info: switch1_info,
                port: switch1_port,
            }
        )
    }
    pub fn print_all_switch() {
        let all_switch_data = Self::new();

        if let Some(switch1_data) = all_switch_data.switch1 {
            println!("TOF-SWITCH1");
            print_switch_data(&switch1_data);
        } else {
            println!("TOF-SWITCH1 is not connected.");
        }

        if let Some(switch2_data) = all_switch_data.switch2 {
            println!("TOF-SWITCH2");
            print_switch_data(&switch2_data);
        } else {
            println!("TOF-SWITCH2 is not connected.");
        }

        if let Some(switch3_data) = all_switch_data.switch3 {
            println!("TOF-SWITCH3");
            print_switch_data(&switch3_data);
        } else {
            println!("TOF-SWITCH3 is not connected.");
        }
    }
}

pub fn clear_port_statistics_all() -> Result<(), SwitchError> {
    
    clear_port_statistics(SWITCH1_ADDRESS)?;
    clear_port_statistics(SWITCH2_ADDRESS)?;
    clear_port_statistics(SWITCH3_ADDRESS)?;

    Ok(())
}