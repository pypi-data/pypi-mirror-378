use crate::constant::*;
use crate::helper::rb_type::{RBVcp, RBError};
use crate::device::{ina226, max11645, pca9548a};

impl RBVcp {
    pub fn new() -> Self {
        match Self::read_vcp() {
            Ok(rb_vcp) => {
                rb_vcp
            }
            Err(_) => {
                Self {
                    zynq_vcp: [f32::MAX; 3],
                    p3v3_vcp: [f32::MAX; 3],
                    p3v5_vcp: [f32::MAX; 3],
                    n1v5_vcp: [f32::MAX; 3],
                    drs_dvdd_vcp: [f32::MAX; 3],
                    drs_avdd_vcp: [f32::MAX; 3],
                    adc_dvdd_vcp: [f32::MAX; 3],
                    adc_avdd_vcp: [f32::MAX; 3],
                }
            }
        }
    }
    pub fn read_vcp() -> Result<RBVcp, RBError> {
        let i2c_mux_1 = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
        let i2c_mux_2 = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);

        i2c_mux_1.select(RB_ZYNQ_INA226_CHANNEL)?;
        let zynq_ina226 = ina226::INA226::new(I2C_BUS, RB_ZYNQ_INA226_ADDRESS, RB_ZYNQ_INA226_RSHUNT, RB_ZYNQ_INA226_MEC,);
        zynq_ina226.configure()?;
        let zynq_vcp = zynq_ina226.read()?;

        i2c_mux_1.select(RB_P3V3_INA226_CHANNEL)?;
        let p3v3_ina226 = ina226::INA226::new(I2C_BUS, RB_P3V3_INA226_ADDRESS, RB_P3V3_INA226_RSHUNT, RB_P3V3_INA226_MEC);
        p3v3_ina226.configure()?;
        let p3v3_vcp =p3v3_ina226.read()?;

        i2c_mux_1.select(RB_P3V5_INA226_CHANNEL)?;
        let p3v5_ina226 = ina226::INA226::new(I2C_BUS, RB_P3V5_INA226_ADDRESS, RB_P3V5_INA226_RSHUNT, RB_P3V5_INA226_MEC);
        p3v5_ina226.configure()?;
        let p3v5_vcp = p3v5_ina226.read()?;

        i2c_mux_1.select(RB_MAX11645_CHANNEL)?;
        let max11645 = max11645::MAX11645::new(I2C_BUS, RB_MAX11645_ADDRESS);
        max11645.setup()?;
        let n1v5_voltage = max11645.read(RB_N1V5_VOLTAGE_INA200_CHANNEL)? * -1.0;
        let n1v5_current = max11645.read(RB_N1V5_CURRENT_INA200_CHANNEL)? / 20.0 / 0.039;
        let n1v5_power = n1v5_voltage.abs() * n1v5_current;
        let n1v5_vcp = [n1v5_voltage, n1v5_current, n1v5_power];

        i2c_mux_1.select(RB_DRS_DVDD_INA226_CHANNEL)?;
        let drs_dvdd_ina226 = ina226::INA226::new(I2C_BUS, RB_DRS_DVDD_INA226_ADDRESS, RB_DRS_DVDD_INA226_RSHUNT, RB_DRS_DVDD_INA226_MEC);
        drs_dvdd_ina226.configure()?;
        let drs_dvdd_vcp = drs_dvdd_ina226.read()?;

        i2c_mux_2.select(RB_DRS_AVDD_INA226_CHANNEL)?;
        let drs_avdd_ina226 = ina226::INA226::new(I2C_BUS, RB_DRS_AVDD_INA226_ADDRESS, RB_DRS_AVDD_INA226_RSHUNT, RB_DRS_AVDD_INA226_MEC);
        drs_avdd_ina226.configure()?;
        let drs_avdd_vcp = drs_avdd_ina226.read()?;

        i2c_mux_2.select(RB_ADC_DVDD_INA226_CHANNEL)?;
        let adc_dvdd_ina226 = ina226::INA226::new(I2C_BUS, RB_ADC_DVDD_INA226_ADDRESS, RB_ADC_DVDD_INA226_RSHUNT, RB_ADC_DVDD_INA226_MEC);
        adc_dvdd_ina226.configure()?;
        let adc_dvdd_vcp = adc_dvdd_ina226.read()?;

        i2c_mux_2.select(RB_ADC_AVDD_INA226_CHANNEL)?;
        let adc_avdd_ina226 = ina226::INA226::new(I2C_BUS, RB_ADC_AVDD_INA226_ADDRESS, RB_ADC_AVDD_INA226_RSHUNT, RB_ADC_AVDD_INA226_MEC);
        adc_avdd_ina226.configure()?;
        let adc_avdd_vcp = adc_avdd_ina226.read()?;

        i2c_mux_1.reset()?;
        i2c_mux_2.reset()?;

        Ok(
            RBVcp {
                zynq_vcp,
                p3v3_vcp,
                p3v5_vcp,
                n1v5_vcp,
                drs_dvdd_vcp,
                drs_avdd_vcp,
                adc_dvdd_vcp,
                adc_avdd_vcp,
            }
        )

    }
}

pub fn config_vcp() -> Result<(), RBError> {
    let i2c_mux_1 = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
    let i2c_mux_2 = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);

    i2c_mux_1.select(RB_DRS_DVDD_INA226_CHANNEL)?;
    let drs_dvdd_ina226 = ina226::INA226::new(
        I2C_BUS,
        RB_DRS_DVDD_INA226_ADDRESS,
        RB_DRS_DVDD_INA226_RSHUNT,
        RB_DRS_DVDD_INA226_MEC,
    );
    for _ in 0..3 {
        drs_dvdd_ina226.configure()?;
        drs_dvdd_ina226.read()?;
    }

    i2c_mux_1.select(RB_P3V3_INA226_CHANNEL)?;
    let p3v3_ina226 = ina226::INA226::new(
        I2C_BUS,
        RB_P3V3_INA226_ADDRESS,
        RB_P3V3_INA226_RSHUNT,
        RB_P3V3_INA226_MEC,
    );
    for _ in 0..3 {
        p3v3_ina226.configure()?;
        p3v3_ina226.read()?;
    }

    i2c_mux_1.select(RB_ZYNQ_INA226_CHANNEL)?;
    let zynq_ina226 = ina226::INA226::new(
        I2C_BUS,
        RB_ZYNQ_INA226_ADDRESS,
        RB_ZYNQ_INA226_RSHUNT,
        RB_ZYNQ_INA226_MEC,
    );
    zynq_ina226.configure()?;
    zynq_ina226.read()?;
    zynq_ina226.read()?;

    i2c_mux_1.select(RB_P3V5_INA226_CHANNEL)?;
    let p3v5_ina226 = ina226::INA226::new(
        I2C_BUS,
        RB_P3V5_INA226_ADDRESS,
        RB_P3V5_INA226_RSHUNT,
        RB_P3V5_INA226_MEC,
    );
    for _ in 0..3 {
        p3v5_ina226.configure()?;
        p3v5_ina226.read()?;
    }

    i2c_mux_2.select(RB_ADC_DVDD_INA226_CHANNEL)?;
    let adc_dvdd_ina226 = ina226::INA226::new(
        I2C_BUS,
        RB_ADC_DVDD_INA226_ADDRESS,
        RB_ADC_DVDD_INA226_RSHUNT,
        RB_ADC_DVDD_INA226_MEC,
    );
    for _ in 0..3 {
        adc_dvdd_ina226.configure()?;
        adc_dvdd_ina226.read()?;
    }

    i2c_mux_2.select(RB_ADC_AVDD_INA226_CHANNEL)?;
    let adc_avdd_ina226 = ina226::INA226::new(
        I2C_BUS,
        RB_ADC_AVDD_INA226_ADDRESS,
        RB_ADC_AVDD_INA226_RSHUNT,
        RB_ADC_AVDD_INA226_MEC,
    );
    for _ in 0..3 {
        adc_avdd_ina226.configure()?;
        adc_avdd_ina226.read()?;
    }

    i2c_mux_2.select(RB_DRS_AVDD_INA226_CHANNEL)?;
    let drs_avdd_ina226 = ina226::INA226::new(
        I2C_BUS,
        RB_DRS_AVDD_INA226_ADDRESS,
        RB_DRS_AVDD_INA226_RSHUNT,
        RB_DRS_AVDD_INA226_MEC,
    );
    for _ in 0..3 {
        drs_avdd_ina226.configure()?;
        drs_avdd_ina226.read()?;
    }

    i2c_mux_1.select(RB_MAX11645_CHANNEL)?;
    let max11645 = max11645::MAX11645::new(I2C_BUS, RB_MAX11645_ADDRESS);
    max11645.setup()?;

    i2c_mux_1.reset()?;
    i2c_mux_2.reset()?;

    Ok(())
}