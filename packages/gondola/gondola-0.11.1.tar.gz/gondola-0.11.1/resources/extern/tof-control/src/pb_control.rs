pub mod pb_init;
pub mod pb_ltb_pwr;
pub mod pb_temp;
pub mod pb_vcp;

// PBMoniData Implementation
use serde_json;
use crate::helper::pb_type::{PBMoniData, PBTemp, PBVcp};

impl PBMoniData {
    pub fn new() -> Self {
        Self {
            pb_temp: PBTemp::new(),
            pb_vcp: PBVcp::new(),
        }
    }
    pub fn print(&self) {
        println!("PB Temperature:");
        println!("{:?}", self.pb_temp);
        println!("PB Voltage, Current and Power:");
        println!("{:?}", self.pb_vcp);
    }
    pub fn print_json(&self) {
        match serde_json::to_string(self) {
            Ok(pb_moni_json) => {
                println!("{}", pb_moni_json);
            }
            Err(e) => {
                eprintln!("PBMoniData JSON Error: {}", e);
            }
        }
    }
}