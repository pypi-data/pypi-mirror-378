pub mod ltb_init;
pub mod ltb_temp;
pub mod ltb_threshold;

// LTBMoniData Implementation
use serde_json;
use crate::helper::ltb_type::{LTBMoniData, LTBTemp, LTBThreshold};

impl LTBMoniData {
    pub fn new() -> Self {
        Self {
            ltb_temp: LTBTemp::new(),
            ltb_thresh: LTBThreshold::new(),
        }
    }
    pub fn print(&self) {
        println!("LTB Temperature:");
        println!("{:?}", self.ltb_temp);
        println!("LTB Threshold:");
        println!("{:?}", self.ltb_thresh);
    }
    pub fn print_json(&self) {
        match serde_json::to_string(self) {
            Ok(ltb_moni_json) => {
                println!("{}", ltb_moni_json);
            }
            Err(e) => {
                eprintln!("LTBMoniData JSON Error: {}", e);
            }
        }
    }
}