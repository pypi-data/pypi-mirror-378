use crate::constant::*;
use crate::helper::tcpc_type::{TCPCVcp, TCPCVcpError};
use crate::device::ina219;

impl TCPCVcp {
    pub fn new() -> Self {
        match Self::read_vcp() {
            Ok(tcpc_vcp) => {
                tcpc_vcp
            }
            Err(_) => {
                Self {
                    tcpc_vcp: [f32::MAX; 3],
                }
            }
        }
    }
    pub fn read_vcp() -> Result<TCPCVcp, TCPCVcpError> {
        let tcpc_ina219 = ina219::INA219::new(1, TCPC_INA219_ADDRESS, TCPC_INA219_RSHUNT, TCPC_INA219_MEC);
        tcpc_ina219.configure()?;
        let tcpc_vcp = tcpc_ina219.read()?;

        Ok(
            TCPCVcp {
                tcpc_vcp,
            }
        )
    }
}