use crate::constant::*;
use crate::helper::cpc_type::{CPCTemp, CPCTempError};
use crate::device::tmp1075;

impl CPCTemp {
    pub fn new() -> Self {
        match Self::read_temp() {
            Ok(cpc_temp) => {
                cpc_temp
            }
            Err(_) => {
                Self {
                    cpc_temp: f32::MAX,
                }
            }
        }
    }
    pub fn read_temp() -> Result<CPCTemp, CPCTempError> {
        let cpc_tmp1075 = tmp1075::TMP1075::new(6, CPC_TMP1075_ADDRESS);
        cpc_tmp1075.config()?;
        let cpc_temp = cpc_tmp1075.read()?;

        Ok(
            CPCTemp {
                cpc_temp,
            }
        )
    }
}