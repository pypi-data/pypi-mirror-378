use sysinfo::{System, SystemExt, DiskExt, CpuExt, RefreshKind, CpuRefreshKind};
// use std::{thread, time::Duration};

use crate::helper::cpu_type::{CPUInfo, CPUInfoDebug};

impl CPUInfo {
    pub fn new() -> Self {
        let cpu_info = Self::read_info();

        cpu_info
    }
    pub fn read_info() -> CPUInfo {
        let mut sys = System::new_all();

        let uptime = Self::read_uptime(&mut sys);
        let cpu_freq = Self::read_cpu_freq(&mut sys);
        let disk_usage = Self::read_disk_usage(&mut sys);
        let root_usage = disk_usage[0];
        let tofdata_usage = disk_usage[1];

        CPUInfo {
            uptime,
            cpu_freq,
            root_usage,
            tofdata_usage,
        }
    }
    pub fn read_uptime(sys: &System) -> u32 {
        let uptime = sys.uptime() as u32;

        uptime
    }
    pub fn read_cpu_freq(sys: &System) -> [u32; 4] {
        let mut cpu0_freq: u32 = Default::default();
        let mut cpu1_freq: u32 = Default::default();
        let mut cpu2_freq: u32 = Default::default();
        let mut cpu3_freq: u32 = Default::default();
        for cpu in sys.cpus() {
            let cpu_name = cpu.name();
            match cpu_name {
                "cpu0" => {
                    cpu0_freq = cpu.frequency() as u32;
                }
                "cpu1" => {
                    cpu1_freq = cpu.frequency() as u32;
                }
                "cpu2" => {
                    cpu2_freq = cpu.frequency() as u32;
                }
                "cpu3" => {
                    cpu3_freq = cpu.frequency() as u32;
                }
                _ => {}
            }
        }

        let cpu_freq = [cpu0_freq, cpu1_freq, cpu2_freq, cpu3_freq];

        cpu_freq
    }
    pub fn read_ram_usage(sys: &System) {
        let used_ram = sys.used_memory();
        let total_ram = sys.total_memory();
        let memory_usage = (used_ram as f32 / total_ram as f32) * 100.0;
        println!("Used RAM: {}MB", used_ram/1000000);
        println!("Total RAM: {}MB", total_ram/1000000);
        println!("Memory Usage: {}%", memory_usage);
    }
    pub fn read_disk_usage(sys: &System) -> [u8; 2] {
        let mut root_usage: u32 = Default::default();
        let mut tofdata_usage: u32 = Default::default();
        for disk in sys.disks() {
            let mut usage = 1.0 - disk.available_space() as f32 / disk.total_space() as f32;
            usage = usage * 100.0;
            let mounted_point = disk.mount_point().as_os_str();
            if mounted_point == "/" {
                root_usage = usage as u32;
            } else if mounted_point == "/tofdata" {
                tofdata_usage = usage as u32;
            } else if mounted_point == "/tpool/tofdata" {
                tofdata_usage = usage as u32;
            }
        }

        // println!("/ Usage: {:?}%", root_usage);
        // println!("/tofdata Usage: {:?}%", tofdata_usage);

        // let disk_usage: f32 = (1.0 - (available_space as f32 / total_space as f32)) * 100.0;
        // println!("{}", disk_usage);
        // disk_usage as u8
        [root_usage as u8, tofdata_usage as u8]
    }
    
}

impl CPUInfoDebug {
    pub fn new() -> Self {
        let cpu_info = Self::read_info();

        cpu_info
    }
    pub fn read_info() -> CPUInfoDebug {
        let mut sys = System::new_all();

        let uptime = Self::read_uptime(&mut sys);
        let disk_usage = Self::read_disk_usage(&mut sys);
        // Self::read_cpu_load(&mut sys);
        // Self::read_cpu_load();
        // sys.refresh_cpu();
        let cpu_freq = Self::read_cpu_freq(&mut sys);

        CPUInfoDebug {
            uptime,
            disk_usage,
            cpu_freq,
        }
    }
    pub fn read_uptime(sys: &System) -> u32 {
        let uptime = sys.uptime() as u32;

        uptime
    }
    // FIXME - hardcoded mountpoint for tofdata (data drive)
    pub fn read_disk_usage(sys: &System) -> u8 {
        let mut available_space = Default::default();
        let mut total_space = Default::default();
        for disk in sys.disks() {
            if disk.mount_point().as_os_str() == "/tofdata" {
                available_space = disk.available_space();
                total_space = disk.total_space();
            }
        }

        let disk_usage: f32 = (1.0 - (available_space as f32 / total_space as f32)) * 100.0;

        disk_usage as u8
    }
    // pub fn read_cpu_load(sys: &mut System) {
    pub fn read_cpu_load() {
        // println!("{:?}", sys.cpus());
        // println!("Load Average: {:?}", sys.load_average());
        // let cpu0_load = sys.load_average();
        let mut sys = System::new_with_specifics(RefreshKind::new().with_cpu(CpuRefreshKind::everything()));
        // sys.refresh_cpu_specifics(CpuRefreshKind::everything());
        // for cpu in sys.cpus() {
        //     cpu.cpu_usage();
        // }
        let mut l = 0;
        while l < 4 {
            sys.refresh_cpu_specifics(CpuRefreshKind::everything());
            for cpu in sys.cpus() {
                println!("Usage: {:?}", cpu.cpu_usage());
                println!("Frequency: {:?}", cpu.frequency());
            }
            l += 1;
            // thread::sleep(Duration::from_millis(1000));
        }
        // sys.refresh_cpu_specifics(CpuRefreshKind::everything());
        // for cpu in sys.cpus() {
        //     println!("Usage: {:?}", cpu.cpu_usage());
        //     println!("Frequency: {:?}", cpu.frequency());
        // }
    }
    pub fn read_cpu_freq(sys: &System) -> [u32; 4] {
        let mut cpu0_freq: u32 = Default::default();
        let mut cpu1_freq: u32 = Default::default();
        let mut cpu2_freq: u32 = Default::default();
        let mut cpu3_freq: u32 = Default::default();
        for cpu in sys.cpus() {
            let cpu_name = cpu.name();
            match cpu_name {
                "cpu0" => {
                    cpu0_freq = cpu.frequency() as u32;
                }
                "cpu1" => {
                    cpu1_freq = cpu.frequency() as u32;
                }
                "cpu2" => {
                    cpu2_freq = cpu.frequency() as u32;
                }
                "cpu3" => {
                    cpu3_freq = cpu.frequency() as u32;
                }
                _ => {}
            }
        }

        let cpu_freq = [cpu0_freq, cpu1_freq, cpu2_freq, cpu3_freq];

        cpu_freq
    }
}
