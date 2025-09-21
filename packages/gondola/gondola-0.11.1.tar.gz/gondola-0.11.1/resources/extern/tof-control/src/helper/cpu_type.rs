use serde::{Deserialize, Serialize};

#[derive(Debug)]
pub struct CPUInfo {
    pub uptime: u32,
    pub cpu_freq: [u32; 4],
    pub root_usage: u8,
    pub tofdata_usage: u8,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CPUInfoDebug {
    pub uptime: u32,
    pub disk_usage: u8,
    pub cpu_freq: [u32; 4],
}

#[derive(Debug)]
pub struct CPUTemp {
    pub cpu0_temp: f32,
    pub cpu1_temp: f32,
}
#[derive(Debug, Serialize, Deserialize)]
pub struct CPUTempDebug {
    pub cpu_temp: f32,
    pub cpu0_temp: f32,
    pub cpu1_temp: f32,
    pub mb_temp: f32,
}