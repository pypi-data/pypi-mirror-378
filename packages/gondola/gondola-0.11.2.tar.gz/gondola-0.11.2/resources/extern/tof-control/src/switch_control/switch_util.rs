use snmp::{SyncSession, Value};

use crate::helper::switch_type::{SwitchData, SwitchError};

pub fn convert_oid(oid_str: &str) -> Result<Vec<u32>, SwitchError> {
    let mut oid_trim = oid_str.trim();
    oid_trim = oid_trim.chars().next().map(|c| &oid_trim[c.len_utf8()..]).unwrap_or(oid_trim);
    let oid_char: Vec<&str> = oid_trim.split(".").collect();

    let mut oid: Vec<u32> = Default::default();
    for c in oid_char {
        oid.push(c.parse::<u32>()?);
    }

    Ok(oid)
}

pub fn snmp_get_integer(oid_str: &str, session: &mut SyncSession) -> Result<i64, SwitchError> {
    let oid = convert_oid(oid_str)?;
    let mut response = session.getnext(&oid)?;
    let mut value: i64 = Default::default();
    if let Some((_oid, Value::Integer(sys_descr))) = response.varbinds.next() {
        value = sys_descr;
    }

    Ok(value)
}

pub fn snmp_get_unsigned32(oid_str: &str, session: &mut SyncSession) -> Result<u32, SwitchError> {
    let oid = convert_oid(oid_str)?;
    let mut response = session.getnext(&oid)?;
    let mut value: u32 = Default::default();
    if let Some((_oid, Value::Unsigned32(sys_descr))) = response.varbinds.next() {
        value = sys_descr;
    }

    Ok(value)
}

pub fn snmp_get_octetstring(oid_str: &str, session: &mut SyncSession) -> Result<String, SwitchError> {
    let oid = convert_oid(oid_str)?;
    let mut response = session.getnext(&oid)?;
    let mut value: String = Default::default();
    if let Some((_oid, Value::OctetString(sys_descr))) = response.varbinds.next() {
        value = String::from_utf8_lossy(sys_descr).to_string();
    }

    Ok(value)
}

pub fn snmp_get_octetstring_raw(oid_str: &str, session: &mut SyncSession) -> Result<Vec<u8>, SwitchError> {
    let oid = convert_oid(oid_str)?;
    let mut response = session.getnext(&oid)?;
    let mut value: Vec<u8>  = Default::default();
    if let Some((_oid, Value::OctetString(sys_descr))) = response.varbinds.next() {
        // let value = String::from_utf8_lossy(sys_descr).to_string();
        value = sys_descr.to_vec();
    }

    Ok(value)
}

pub fn snmp_getbulk_integer(oid_str: &str, session: &mut SyncSession) -> Result<[u8; 16], SwitchError> {
    let oid = convert_oid(oid_str)?;
    let response = session.getbulk(&[&oid], 0, 16)?;

    let mut values: [u8; 16] = Default::default();

    for (i, varbind) in response.varbinds.enumerate() {
        if let (_oid, Value::Integer(val)) = varbind {
            values[i] = val as u8;
        }
    }

    Ok(values)
}

pub fn snmp_getbulk_counter64(oid_str: &str, session: &mut SyncSession) -> Result<[u64; 16], SwitchError> {
    let oid = convert_oid(oid_str)?;
    let response = session.getbulk(&[&oid], 0, 16)?;

    let mut values: [u64; 16] = Default::default();

    for (i, varbind) in response.varbinds.enumerate() {
        if let (_oid, Value::Counter64(val)) = varbind {
            values[i] = val;
        }
    }

    Ok(values)
}

pub fn print_switch_data(switch: &SwitchData) {
    // Switch Info
    println!("\tHostname:               {}", switch.info.hostname);
    println!("\tUptime:                 {}", switch.info.uptime);
    println!("\tMac Address:            {}", switch.info.mac_address);
    println!("\tCPU Load Avg:           {:?}", switch.info.cpu_load);
    println!("\tPower Supply Status:    {:?}", switch.info.ps_status);
    // Switch Port
    println!("\tLink:                   {:?}", switch.port.link);
    println!("\tSpeed:                  {:?}", switch.port.speed);
    println!("\tFull Duplex:            {:?}", switch.port.full_duplex);
    println!("\tRx Bytes:               {:?}", switch.port.rx_bytes);
    println!("\tRx Packets:             {:?}", switch.port.rx_pkts);
    println!("\tRx Dropped Events:      {:?}", switch.port.rx_drop_evts);
    println!("\tRx Broadcast Packets:   {:?}", switch.port.rx_broadcast_pkts);
    println!("\tRx Multicast Packets:   {:?}", switch.port.rx_multicast_pkts);
    println!("\tRx CRC Error Packets:   {:?}", switch.port.rx_crc_align_err_pkts);
    println!("\tTx Bytes:               {:?}", switch.port.tx_bytes);
    println!("\tTx Packets:             {:?}", switch.port.tx_pkts);
    println!("\tTx Dropped Events:      {:?}", switch.port.tx_drop_evts);
    println!("\tTx Broadcast Packets:   {:?}", switch.port.tx_broadcast_pkts);
    println!("\tTx Multicast Packets:   {:?}", switch.port.tx_multicast_pkts);
}

pub fn snmp_set_integer(oid_str: &str, value: i64, session: &mut SyncSession) -> Result<(), SwitchError> {
    let oid = convert_oid(oid_str)?;
    let _response = session.set(&[(&oid, Value::Integer(value))])?;

    Ok(())
}