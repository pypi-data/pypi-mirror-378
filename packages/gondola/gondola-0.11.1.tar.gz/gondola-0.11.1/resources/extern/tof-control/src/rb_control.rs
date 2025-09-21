pub mod rb_clk;
pub mod rb_config;
pub mod rb_dac;
pub mod rb_gpioe;
pub mod rb_info;
pub mod rb_init;
pub mod rb_input;
pub mod rb_mag;
pub mod rb_mode;
pub mod rb_ph;
pub mod rb_temp;
pub mod rb_vcp;
pub mod rb_reset;

// RBMoniData Implementation
use serde_json;
use crate::helper::rb_type::{RBMoniData, RBInfo, RBTemp, RBVcp, RBPh, RBMag};

impl RBMoniData {
    pub fn new() -> Self {
        Self {
            rb_info: RBInfo::new(),
            rb_temp: RBTemp::new(),
            rb_vcp: RBVcp::new(),
            rb_ph: RBPh::new(),
            rb_mag: RBMag::new(),
        }
    }
    pub fn print(&self) {
        println!("RB Information:");
        println!("{:?}", self.rb_info);
        println!("RB Temperature:");
        println!("{:?}", self.rb_temp);
        println!("RB Voltage, Current and Power:");
        println!("{:?}", self.rb_vcp);
        println!("RB Humidity and Pressure:");
        println!("{:?}", self.rb_ph);
        println!("RB Magnetic Field:");
        println!("{:?}", self.rb_mag);
    }
    pub fn print_json(&self) {
        match serde_json::to_string(self) {
            Ok(rb_moni_json) => {
                println!("{}", rb_moni_json);
            }
            Err(e) => {
                eprintln!("RBMoniData JSON Error: {}", e);
            }
        }
    }
}