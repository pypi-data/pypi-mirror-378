pub mod pa_bias;
pub mod pa_init;
pub mod pa_temp;

// PAMoniData Implementation
use serde_json;
use crate::helper::pa_type::{PAMoniData, PATemp, PAReadBias};

impl PAMoniData {
    pub fn new() -> Self {
        Self {
            pa_temp: PATemp::new(),
            pa_bias: PAReadBias::new(),
        }
    }
    pub fn print(&self) {
        println!("PA Temperature:");
        println!("{:?}", self.pa_temp);
        println!("PA SiPM Bias Voltage:");
        println!("{:?}", self.pa_bias);
    }
    pub fn print_json(&self) {
        match serde_json::to_string(self) {
            Ok(pa_moni_json) => {
                println!("{}", pa_moni_json);
            }
            Err(e) => {
                eprintln!("PAMoniData JSON Error: {}", e);
            }
        }
    }
}