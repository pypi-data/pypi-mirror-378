use snmp::SyncSession;
use std::time::Duration;

use crate::helper::switch_type::{SwitchInfo, SwitchError};
use super::switch_util::{snmp_get_integer, snmp_get_unsigned32, snmp_get_octetstring, snmp_get_octetstring_raw};

impl SwitchInfo {
    pub fn new(ip_addr: &str) -> Self {
        match Self::read_info(ip_addr) {
            Ok(switch_info) => {
                switch_info
            }
            Err(_) => {
                Self {
                    hostname: "".to_string(),
                    uptime: "".to_string(),
                    mac_address: "".to_string(),
                    cpu_load: [u8::MAX, u8::MAX, u8::MAX],
                    ps_status: [u8::MAX, u8::MAX],
                }
            }
        }
    }
    pub fn read_info(ip_addr: &str) -> Result<SwitchInfo, SwitchError> {
        let mut snmp_session = SyncSession::new(ip_addr, b"public", Some(Duration::from_secs(2)), 0)?;

        let hostname = Self::read_hostname(&mut snmp_session)?;
        let uptime = Self::read_uptime(&mut snmp_session)?;
        let mac_address = Self::read_mac_address(&mut snmp_session)?;
        let cpu_load = Self::read_cpu_load(&mut snmp_session)?;
        let ps_status = Self::read_ps_status(&mut snmp_session)?;

        Ok(
            SwitchInfo {
                hostname,
                uptime,
                mac_address,
                cpu_load,
                ps_status,
            }
        )
    }
    pub fn read_hostname(session: &mut SyncSession) -> Result<String, SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.24.1.2.1.1";
        let hostname = snmp_get_octetstring(oid, session)?;

        Ok(hostname)
    }
    pub fn read_uptime(session: &mut SyncSession) -> Result<String, SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.24.1.3.4.1";
        let uptime = snmp_get_octetstring(oid, session)?;

        Ok(uptime)
    }
    pub fn read_mac_address(session: &mut SyncSession) -> Result<String, SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.24.1.3.5.1";
        let mac_address_vec = snmp_get_octetstring_raw(oid, session)?;
        let mut mac_address: String = Default::default();
        let mut vec_len = mac_address_vec.len();
        for octet in mac_address_vec.iter() {
            let octet_hex = format!("{:02X}", octet);
            if vec_len == 1 {
                mac_address = mac_address + &octet_hex;
            } else {
                mac_address = mac_address + &octet_hex + "-";
                vec_len -= 1;
            }
        }
        
        Ok(mac_address)
    }
    pub fn read_cpu_load(session: &mut SyncSession) -> Result<[u8; 3], SwitchError> {
        let oid_100ms = ".1.3.6.1.4.1.38477.1.50.1.24.1.3.1.1";
        let oid_1s = ".1.3.6.1.4.1.38477.1.50.1.24.1.3.1.2";
        let oid_10s = ".1.3.6.1.4.1.38477.1.50.1.24.1.3.1.3";

        let cpu_load_avg_100ms = snmp_get_unsigned32(oid_100ms, session)? as u8;
        let cpu_load_avg_1s = snmp_get_unsigned32(oid_1s, session)? as u8;
        let cpu_load_avg_10s = snmp_get_unsigned32(oid_10s, session)? as u8;

        Ok([cpu_load_avg_100ms, cpu_load_avg_1s, cpu_load_avg_10s])
    }
    pub fn read_ps_status(session: &mut SyncSession) -> Result<[u8; 2], SwitchError> {
        let oid_main = ".1.3.6.1.4.1.38477.1.50.1.24.1.3.2.1.3.1.1";
        let oid_redundant = ".1.3.6.1.4.1.38477.1.50.1.24.1.3.2.1.3.1.2";

        let main_ps_status = snmp_get_integer(oid_main, session)? as u8;
        let redundant_ps_status = snmp_get_integer(oid_redundant, session)? as u8;

        Ok([main_ps_status, redundant_ps_status])
    }
    // pub fn print_switch_info(ip_addr: &str) {
    //     let switch_info = Self::new(ip_addr);

    //     println!("Switch Info");
    //     println!("\tHostname:       {}", switch_info.hostname);
    //     println!("\tUptime:         {}", switch_info.uptime);
    //     println!("\tMac Address:    {}", switch_info.mac_address);
    // }
}