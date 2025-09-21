pub mod constant;
pub mod helper;
pub mod device;
pub mod ltb_control;
pub mod memory;
pub mod pb_control;
pub mod pa_control;
pub mod rb_control;
pub mod cpu_control;
pub mod cpc_control;
pub mod tcpc_control;
pub mod switch_control;
pub mod mtb_control;

// RATMoniData
use serde_json;
use serde::{Deserialize, Serialize};
use crate::helper::{
    rb_type::RBMoniData,
    ltb_type::LTBMoniData,
    pb_type::PBMoniData,
    pa_type::PAMoniData,
};

// RAT Data Type
#[derive(Debug, Serialize, Deserialize)]
pub struct RATMoniData {
    pub rb_data: RBMoniData,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ltb_data: Option<LTBMoniData>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pb_data: Option<PBMoniData>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pa_data: Option<PAMoniData>,
}

impl RATMoniData {
    pub fn new() -> Self {
        let rb_data = RBMoniData::new();
        let sub_board = rb_data.rb_info.sub_board;

        let mut ltb_data = None;
        if sub_board == 1 {
            ltb_data = Some(LTBMoniData::new());
        }

        let mut pb_data = None;
        let mut pa_data = None;
        if sub_board == 2 {
            pb_data = Some(PBMoniData::new());
            pa_data = Some(PAMoniData::new());
        }

        Self {
            rb_data,
            ltb_data,
            pb_data,
            pa_data,
        }
    }
    pub fn print(&self) {
        println!("RB Data:");
        println!("{:?}", &self.rb_data);
        if let Some(ltb_data) = &self.ltb_data {
            println!("LTB Data:");
            println!("{:?}", ltb_data);
        }
        if let Some(pb_data) = &self.pb_data {
            println!("PB Data:");
            println!("{:?}", pb_data);
        }
        if let Some(pa_data) = &self.pa_data {
            println!("PA Data:");
            println!("{:?}", pa_data);
        }
    }
    pub fn print_json(&self) {
        match serde_json::to_string(self) {
            Ok(rat_moni_json) => {
                println!("{}", rat_moni_json);
            }
            Err(e) => {
                eprintln!("RATMoniData JSON Error: {}", e);
            }
        }
    }
}



