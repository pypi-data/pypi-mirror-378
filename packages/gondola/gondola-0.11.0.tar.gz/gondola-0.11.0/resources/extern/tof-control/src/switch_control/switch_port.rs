use snmp::SyncSession;
use std::time::Duration;

use crate::helper::switch_type::{SwitchPort, SwitchError};
use crate::switch_control::switch_util::{snmp_getbulk_integer, snmp_getbulk_counter64, snmp_set_integer};

impl SwitchPort {
    pub fn new(ip_addr: &str) -> Self {
        match Self::read_port(ip_addr) {
            Ok(switch_port) => {
                switch_port
            }
            Err(_) => {
                Self {
                    link: [u8::MAX; 16],
                    speed: [u8::MAX; 16],
                    full_duplex: [u8::MAX; 16],
                    rx_bytes: [u64::MAX; 16],
                    rx_pkts: [u64::MAX; 16],
                    rx_drop_evts: [u64::MAX; 16],
                    rx_broadcast_pkts: [u64::MAX; 16],
                    rx_multicast_pkts: [u64::MAX; 16],
                    rx_crc_align_err_pkts: [u64::MAX; 16],
                    tx_bytes: [u64::MAX; 16],
                    tx_pkts: [u64::MAX; 16],
                    tx_drop_evts: [u64::MAX; 16],
                    tx_broadcast_pkts: [u64::MAX; 16],
                    tx_multicast_pkts: [u64::MAX; 16],
                }
            }
        }
    }
    pub fn read_port(ip_addr: &str) -> Result<SwitchPort, SwitchError> {
        let mut snmp_session = SyncSession::new(ip_addr, b"public", Some(Duration::from_secs(1)), 0)?;

        let link = Self::read_link(&mut snmp_session)?;
        let speed = Self::read_speed(&mut snmp_session)?;
        let full_duplex = Self::read_full_duplex(&mut snmp_session)?;
        let rx_bytes = Self::read_rx_bytes(&mut snmp_session)?;
        let rx_pkts = Self::read_rx_pkts(&mut snmp_session)?;
        let rx_drop_evts = Self::read_rx_drop_evts(&mut snmp_session)?;
        let rx_broadcast_pkts = Self::read_rx_broadcast_pkts(&mut snmp_session)?;
        let rx_multicast_pkts = Self::read_rx_multicast_pkts(&mut snmp_session)?;
        let rx_crc_align_err_pkts = Self::read_rx_crc_align_err_pkts(&mut snmp_session)?;
        let tx_bytes = Self::read_tx_bytes(&mut snmp_session)?;
        let tx_pkts = Self::read_tx_pkts(&mut snmp_session)?;
        let tx_drop_evts = Self::read_tx_drop_evts(&mut snmp_session)?;
        let tx_broadcast_pkts = Self::read_tx_broadcast_pkts(&mut snmp_session)?;
        let tx_multicast_pkts = Self::read_tx_multicast_pkts(&mut snmp_session)?;

        Ok(
            SwitchPort {
                link,
                speed,
                full_duplex,
                rx_bytes,
                rx_pkts,
                rx_drop_evts,
                rx_broadcast_pkts,
                rx_multicast_pkts,
                rx_crc_align_err_pkts,
                tx_bytes,
                tx_pkts,
                tx_drop_evts,
                tx_broadcast_pkts,
                tx_multicast_pkts,
            }
        )
    }
    pub fn read_link(session: &mut SyncSession) -> Result<[u8; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.3.1.1.2";
        let link = snmp_getbulk_integer(oid, session)?;

        Ok(link)
    }
    pub fn read_speed(session: &mut SyncSession) -> Result<[u8; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.3.1.1.5";
        let speed = snmp_getbulk_integer(oid, session)?;

        Ok(speed)
    }
    pub fn read_full_duplex(session: &mut SyncSession) -> Result<[u8; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.3.1.1.3";
        let fdx = snmp_getbulk_integer(oid, session)?;

        Ok(fdx)
    }
    pub fn read_rx_bytes(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.3";
        let rx_bytes = snmp_getbulk_counter64(oid, session)?;

        Ok(rx_bytes)
    }
    pub fn read_rx_pkts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.4";
        let rx_pkts = snmp_getbulk_counter64(oid, session)?;

        Ok(rx_pkts)
    }
    pub fn read_rx_drop_evts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.2";
        let rx_drop_evts = snmp_getbulk_counter64(oid, session)?;

        Ok(rx_drop_evts)
    }
    pub fn read_rx_broadcast_pkts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.5";
        let rx_broadcast_pkts = snmp_getbulk_counter64(oid, session)?;

        Ok(rx_broadcast_pkts)
    }
    pub fn read_rx_multicast_pkts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.6";
        let rx_multicast_pkts = snmp_getbulk_counter64(oid, session)?;

        Ok(rx_multicast_pkts)
    }
    pub fn read_rx_crc_align_err_pkts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.7";
        let rx_crc_align_err_pkts = snmp_getbulk_counter64(oid, session)?;

        Ok(rx_crc_align_err_pkts)
    }
    pub fn read_tx_bytes(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.20";
        let tx_bytes = snmp_getbulk_counter64(oid, session)?;

        Ok(tx_bytes)
    }
    pub fn read_tx_pkts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.21";
        let tx_pkts = snmp_getbulk_counter64(oid, session)?;

        Ok(tx_pkts)
    }
    pub fn read_tx_drop_evts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.19";
        let tx_drop_evts = snmp_getbulk_counter64(oid, session)?;

        Ok(tx_drop_evts)
    }
    pub fn read_tx_broadcast_pkts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.22";
        let tx_broadcast_pkts = snmp_getbulk_counter64(oid, session)?;

        Ok(tx_broadcast_pkts)
    }
    pub fn read_tx_multicast_pkts(session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
        let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.5.1.1.23";
        let tx_multicast_pkts = snmp_getbulk_counter64(oid, session)?;

        Ok(tx_multicast_pkts)
    }

    // pub fn print_switch_port(ip_addr: &str) {
    //     let switch_port = Self::new(ip_addr);

    //     println!("Switch Port");
    //     println!("\tLink:           {:?}", switch_port.link);
    //     println!("\tSpeed:          {:?}", switch_port.speed);
    //     println!("\tFull Duplex:    {:?}", switch_port.full_duplex);
    // }
}

pub fn clear_port_statistics(ip_addr: &str) -> Result<(), SwitchError> {
    let mut snmp_session = SyncSession::new(ip_addr, b"private", Some(Duration::from_secs(1)), 0)?;
    let oid = ".1.3.6.1.4.1.38477.1.50.1.11.1.4.1.1.1.2";
    for i in 1..=16 {
        let sub_oid = (1000000 + i).to_string();
        let oid_port = oid.to_string() + "." + &sub_oid;
        snmp_set_integer(&oid_port, 1, &mut snmp_session)?;
    }

    Ok(())
}