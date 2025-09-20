use crate::constant::*;
use crate::helper::pb_type::{PBVcp, PBError};
use crate::device::{ina219, ina226, max11617, pca9548a};

impl PBVcp {
    pub fn new() -> Self {
        match Self::read_vcp() {
            Ok(pb_vcp) => {
                pb_vcp
            }
            Err(_) => {
                Self {
                    p3v6_pa_vcp: [f32::MAX; 3],
                    n1v6_pa_vcp: [f32::MAX; 3],
                    p3v4f_ltb_vcp: [f32::MAX; 3],
                    p3v4d_ltb_vcp: [f32::MAX; 3],
                    p3v6_ltb_vcp: [f32::MAX; 3],
                    n1v6_ltb_vcp: [f32::MAX; 3],
                }
            }
        }
    }
    pub fn read_vcp() -> Result<PBVcp, PBError> {
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
    
        i2c_mux.select(PB_P3V6_PA_INA226_CHANNEL)?;
        let p3v6_pa_ina226 = ina226::INA226::new(
            I2C_BUS,
            PB_P3V6_PA_INA226_ADDRESS,
            PB_P3V6_PA_INA226_RSHUNT,
            PB_P3V6_PA_INA226_MEC,
        );
        p3v6_pa_ina226.configure()?;
        let p3v6_pa_vcp = p3v6_pa_ina226.read()?;

        i2c_mux.select(PB_ADC_1_CHANNEL)?;
        let max11617 = max11617::MAX11617::new(I2C_BUS, PB_MAX11617_ADDRESS);
        max11617.setup()?;
        let n1v6_pa_voltage = max11617.read(PB_N1V6_PA_VOLTAGE_INA201_CHANNEL)? * -1.0;
        let n1v6_pa_current = max11617.read(PB_N1V6_PA_CURRENT_INA201_CHANNEL)? / 50.0 / 0.1;
        let n1v6_pa_power = n1v6_pa_voltage.abs() * n1v6_pa_current;
        let n1v6_pa_vcp = [n1v6_pa_voltage, n1v6_pa_current, n1v6_pa_power];

        i2c_mux.select(PB_LTB_INA219_CHANNEL)?;
        let p3v4f_ltb_ina219 = ina219::INA219::new(
            I2C_BUS,
            PB_P3V4F_LTB_INA219_ADDRESS,
            PB_P3V4F_LTB_INA219_RSHUNT,
            PB_P3V4F_LTB_INA219_MEC,
        );
        p3v4f_ltb_ina219.configure()?;
        let p3v4f_ltb_vcp = p3v4f_ltb_ina219.read()?;

        let p3v4d_ltb_ina219 = ina219::INA219::new(
            I2C_BUS,
            PB_P3V4D_LTB_INA219_ADDRESS,
            PB_P3V4D_LTB_INA219_RSHUNT,
            PB_P3V4D_LTB_INA219_MEC,
        );
        p3v4d_ltb_ina219.configure()?;
        let p3v4d_ltb_vcp = p3v4d_ltb_ina219.read()?;

        let p3v6_ltb_ina219 = ina219::INA219::new(
            I2C_BUS,
            PB_P3V6_LTB_INA219_ADDRESS,
            PB_P3V6_LTB_INA219_RSHUNT,
            PB_P3V6_LTB_INA219_MEC,
        );
        p3v6_ltb_ina219.configure()?;
        let p3v6_ltb_vcp = p3v6_ltb_ina219.read()?;

        i2c_mux.select(PB_ADC_2_CHANNEL)?;
        let max11617 = max11617::MAX11617::new(I2C_BUS, PB_MAX11617_ADDRESS);
        max11617.setup()?;
        let n1v6_ltb_voltage = max11617.read(PB_N1V6_LTB_VOLTAGE_INA202_CHANNEL)? * -1.0;
        let n1v6_ltb_current = max11617.read(PB_N1V6_LTB_CURRENT_INA202_CHANNEL)? / 100.0 / 0.1;
        let n1v6_ltb_power = n1v6_ltb_voltage.abs() * n1v6_ltb_current;
        let n1v6_ltb_vcp = [n1v6_ltb_voltage, n1v6_ltb_current, n1v6_ltb_power];

        i2c_mux.reset()?;

        Ok(
            PBVcp {
                p3v6_pa_vcp,
                n1v6_pa_vcp,
                p3v4f_ltb_vcp,
                p3v4d_ltb_vcp,
                p3v6_ltb_vcp,
                n1v6_ltb_vcp,
            }
        )
    }
}

pub fn config_vcp() -> Result<(), PBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
    
    i2c_mux.select(PB_P3V6_PA_INA226_CHANNEL)?;
    let p3v6_pa_ina226 = ina226::INA226::new(
        I2C_BUS,
        PB_P3V6_PA_INA226_ADDRESS,
        PB_P3V6_PA_INA226_RSHUNT,
        PB_P3V6_PA_INA226_MEC,
    );
    for _ in 0..3 {
        p3v6_pa_ina226.configure()?;
        p3v6_pa_ina226.read()?;
    }

    i2c_mux.select(PB_ADC_1_CHANNEL)?;
    let max11617 = max11617::MAX11617::new(I2C_BUS, PB_MAX11617_ADDRESS);
    max11617.setup()?;

    i2c_mux.select(PB_LTB_INA219_CHANNEL)?;
    let p3v4f_ltb_ina219 = ina219::INA219::new(
        I2C_BUS,
        PB_P3V4F_LTB_INA219_ADDRESS,
        PB_P3V4F_LTB_INA219_RSHUNT,
        PB_P3V4F_LTB_INA219_MEC,
    );
    for _ in 0..3 {
        p3v4f_ltb_ina219.configure()?;
        p3v4f_ltb_ina219.read()?;
    }

    let p3v4d_ltb_ina219 = ina219::INA219::new(
        I2C_BUS,
        PB_P3V4D_LTB_INA219_ADDRESS,
        PB_P3V4D_LTB_INA219_RSHUNT,
        PB_P3V4D_LTB_INA219_MEC,
    );
    for _ in 0..3 {
        p3v4d_ltb_ina219.configure()?;
        p3v4d_ltb_ina219.read()?;
    }

    let p3v6_ltb_ina219 = ina219::INA219::new(
        I2C_BUS,
        PB_P3V6_LTB_INA219_ADDRESS,
        PB_P3V6_LTB_INA219_RSHUNT,
        PB_P3V6_LTB_INA219_MEC,
    );
    for _ in 0..3 {
        p3v6_ltb_ina219.configure()?;
        p3v6_ltb_ina219.read()?;
    }

    i2c_mux.select(PB_ADC_2_CHANNEL)?;
    let max11617 = max11617::MAX11617::new(I2C_BUS, PB_MAX11617_ADDRESS);
    max11617.setup()?;

    i2c_mux.reset()?;

    Ok(())
}