#[derive(Debug)]
pub struct AllSwitchData {
    pub switch1: Option<SwitchData>,
    pub switch2: Option<SwitchData>,
    pub switch3: Option<SwitchData>,
}

#[derive(Debug)]
pub struct SwitchData {
    pub info: SwitchInfo,
    pub port: SwitchPort,
}

#[derive(Debug)]
pub struct SwitchInfo {
    pub hostname: String,
    pub uptime: String, // VTSSDisplayString (OCTET STRING) (SIZE(0..10)). Hint: 255a
    pub mac_address: String,
    pub cpu_load: [u8; 3], // [100ms, 1s, 10s]
    // Need to Check!
    pub ps_status: [u8; 2], // vtssSysutilStatusPowerSupplyState (INTEGER), VTSSSysutilPowerSupplyStateType (INTEGER) {active(0), standby(1), notPresent(2) }, The state of power supply.
}

#[derive(Debug)]
pub struct SwitchPort {
    pub link: [u8; 16], // TruthValue (INTEGER) {true(1), false(2) }
    pub speed: [u8; 16], // VTSSPortStatusSpeed (INTEGER) {undefined(0), speed10M(1), speed100M(2), speed1G(3), speed2G5(4), speed5G(5), speed10G(6), speed12G(7) }
    pub full_duplex: [u8; 16], // TruthValue (INTEGER) {true(1), false(2) }
    pub rx_bytes: [u64; 16], // vtssPortStatisticsRmonStatisticsRxOctets (COUNTER64), Shows the number of received (good and bad) bytes. Includes FCS, but excludes framing bits.
    pub rx_pkts: [u64; 16], // vtssPortStatisticsRmonStatisticsRxPkts (COUNTER64), Shows the number of received (good and bad) packets.
    pub rx_drop_evts: [u64; 16], // vtssPortStatisticsRmonStatisticsRxDropEvents (COUNTER64), Shows the number of frames discarded due to ingress congestion.
    pub rx_broadcast_pkts: [u64; 16], // vtssPortStatisticsRmonStatisticsRxBroadcastPkts (COUNTER64), Shows the number of received (good and bad) broadcast packets.
    pub rx_multicast_pkts: [u64; 16], // vtssPortStatisticsRmonStatisticsRxMulticastPkts (COUNTER64), Shows the number of received (good and bad) multicast packets.
    pub rx_crc_align_err_pkts: [u64; 16], // vtssPortStatisticsRmonStatisticsRxCrcAlignErrPkts (COUNTER64), Shows the number of frames received with CRC or alignment errors.
    pub tx_bytes: [u64; 16], //  vtssPortStatisticsRmonStatisticsTxOctets (COUNTER64), Shows the number of transmitted (good and bad) bytes. Includes FCS, but excludes framing bits.
    pub tx_pkts: [u64; 16], // vtssPortStatisticsRmonStatisticsTxPkts (COUNTER64), Shows the number of transmitted (good and bad) packets.
    pub tx_drop_evts: [u64; 16], // vtssPortStatisticsRmonStatisticsTxDropEvents (COUNTER64), Shows the number of frames discarded due to egress congestion.
    pub tx_broadcast_pkts: [u64; 16], // vtssPortStatisticsRmonStatisticsTxBroadcastPkts (COUNTER64), Shows the number of transmitted (good and bad) broadcast packets.
    pub tx_multicast_pkts: [u64; 16], // vtssPortStatisticsRmonStatisticsTxMulticastPkts (COUNTER64), Shows the number of transmitted (good and bad) multicast packets.
}

/// Switch Error Type
#[derive(Debug)]
pub enum SwitchError {
    SNMP(snmp::SnmpError),
    ParseInt(std::num::ParseIntError),
    IO(std::io::Error),
    Address,
}

impl From<snmp::SnmpError> for SwitchError {
    fn from(e: snmp::SnmpError) -> Self {
        SwitchError::SNMP(e)
    }
}

impl From<std::num::ParseIntError> for SwitchError {
    fn from(e: std::num::ParseIntError) -> Self {
        SwitchError::ParseInt(e)
    }
}

impl From<std::io::Error> for SwitchError {
    fn from(e: std::io::Error) -> Self {
        SwitchError::IO(e)
    }
}