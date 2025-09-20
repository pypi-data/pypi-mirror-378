use crate::constant::*;
use crate::helper::pb_type::{PBTemp, PBError};
use crate::device::{pca9548a, tmp1075};

impl PBTemp {
    pub fn new() -> Self {
        match Self::read_temp() {
            Ok(pb_temp) => {
                pb_temp
            }
            Err(_) => {
                Self {
                    pds_temp: f32::MAX,
                    pas_temp: f32::MAX,
                    nas_temp: f32::MAX,
                    shv_temp: f32::MAX,
                }
            }
        }
    }

    pub fn read_temp() -> Result<PBTemp, PBError> {
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
        i2c_mux.select(PB_TMP1075_CHANNEL)?;

        // Positive Degital Supply DC-DC Converter Temperature
        let pds_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_PDS_TMP1075_ADDRESS);
        pds_tmp1075.config()?;
        let pds_temp = pds_tmp1075.read()?;

        // Positive Analog Supply DC-DC Converter Temperature
        let pas_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_PAS_TMP1075_ADDRESS);
        pas_tmp1075.config()?;
        let pas_temp = pas_tmp1075.read()?;

        // Negative Analog Supply DC-DC Converter Temperature
        let nas_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_NAS_TMP1075_ADDRESS);
        nas_tmp1075.config()?;
        let nas_temp = nas_tmp1075.read()?;

        // SiPM High Voltage Supply DC-DC Converter Temperature
        let shv_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_SHV_TMP1075_ADDRESS);
        shv_tmp1075.config()?;
        let shv_temp = shv_tmp1075.read()?;

        i2c_mux.reset()?;

        Ok(
            PBTemp {
                pds_temp,
                pas_temp,
                nas_temp,
                shv_temp,
            }
        )

    }
}

pub fn config_temp() -> Result<(), PBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
    i2c_mux.select(PB_TMP1075_CHANNEL)?;

    let pds_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_PDS_TMP1075_ADDRESS);
    pds_tmp1075.config()?;

    let pas_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_PAS_TMP1075_ADDRESS);
    pas_tmp1075.config()?;

    let nas_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_NAS_TMP1075_ADDRESS);
    nas_tmp1075.config()?;

    let shv_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_SHV_TMP1075_ADDRESS);
    shv_tmp1075.config()?;

    i2c_mux.reset()?;

    Ok(())
}

pub fn read_pds_temp() -> Result<f32, PBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
    i2c_mux.select(PB_TMP1075_CHANNEL)?;

    let pds_tmp1075 = tmp1075::TMP1075::new(I2C_BUS, PB_PDS_TMP1075_ADDRESS);
    pds_tmp1075.config()?;
    let pds_temp = pds_tmp1075.read()?;

    i2c_mux.reset()?;

    Ok(pds_temp)
}