use crate::constant::*;
use crate::memory::read_control_reg;
use crate::helper::rb_type::{RBTemp, RBError};
use crate::device::{bme280, lis3mdltr, pca9548a, tmp112};

impl RBTemp {
    pub fn new() -> Self {
        match Self::read_temp() {
            Ok(rb_temp) => {
                rb_temp
            }
            Err(_) => {
                Self {
                    zynq_temp: f32::MAX,
                    drs_temp: f32::MAX,
                    clk_temp: f32::MAX,
                    adc_temp: f32::MAX,
                    bme280_temp: f32::MAX,
                    lis3mdltr_temp: f32::MAX,
                }
            }
        }
        
    }
    pub fn read_temp() -> Result<RBTemp, RBError> {
        let zynq_temp_adc = read_control_reg(RB_TEMP)?;
        let zynq_temp = (((zynq_temp_adc & 4095) as f32 * 503.975) / 4096.0) - 273.15;

        let i2c_mux_1 = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
        let i2c_mux_2 = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);

        i2c_mux_1.select(RB_DRS_TMP112_CHANNEL)?;
        let drs_tmp112 = tmp112::TMP112::new(I2C_BUS, RB_DRS_TMP112_ADDRESS);
        drs_tmp112.config()?;
        let drs_temp = drs_tmp112.read()?;

        i2c_mux_1.select(RB_LIS3MDLTR_CHANNEL)?;
        let lis3mdltr = lis3mdltr::LIS3MDLTR::new(I2C_BUS, RB_LIS3MDLTR_ADDRESS);
        lis3mdltr.configure()?;
        let lis3mdltr_temp = lis3mdltr.read_temp()?;

        i2c_mux_1.select(RB_BME280_CHANNEL)?;
        let bme280 = bme280::BME280::new(I2C_BUS, RB_BME280_ADDRESS);
        bme280.configure()?;
        let bme280_temp = bme280.read_all()?[0];

        i2c_mux_2.select(RB_CLK_TMP112_CHANNEL)?;
        let clk_tmp112 = tmp112::TMP112::new(I2C_BUS, RB_CLK_TMP112_ADDRESS);
        clk_tmp112.config()?;
        let clk_temp = clk_tmp112.read()?;

        i2c_mux_2.select(RB_ADC_TMP112_CHANNEL)?;
        let adc_tmp112 = tmp112::TMP112::new(I2C_BUS, RB_ADC_TMP112_ADDRESS);
        adc_tmp112.config()?;
        let adc_temp = adc_tmp112.read()?;

        i2c_mux_1.reset()?;
        i2c_mux_2.reset()?;

        Ok(
            RBTemp {
                zynq_temp,
                drs_temp,
                clk_temp,
                adc_temp,
                bme280_temp,
                lis3mdltr_temp,
            }
        )
    }
    pub fn read_drs_temp() -> Result<f32, RBError> {
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
        i2c_mux.select(RB_DRS_TMP112_CHANNEL)?;
        let drs_tmp112 = tmp112::TMP112::new(I2C_BUS, RB_DRS_TMP112_ADDRESS);
        drs_tmp112.config()?;
        let drs_temp = drs_tmp112.read()?;

        i2c_mux.reset()?;

        Ok(drs_temp)
    }
}

pub fn config_temp() -> Result<(), RBError> {
    let i2c_mux_1 = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
    let i2c_mux_2 = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);

    i2c_mux_1.select(RB_DRS_TMP112_CHANNEL)?;
    let drs_tmp112 = tmp112::TMP112::new(I2C_BUS, RB_DRS_TMP112_ADDRESS);
    drs_tmp112.config()?;

    i2c_mux_2.select(RB_CLK_TMP112_CHANNEL)?;
    let clk_tmp112 = tmp112::TMP112::new(I2C_BUS, RB_CLK_TMP112_ADDRESS);
    clk_tmp112.config()?;

    i2c_mux_2.select(RB_ADC_TMP112_CHANNEL)?;
    let adc_tmp112 = tmp112::TMP112::new(I2C_BUS, RB_ADC_TMP112_ADDRESS);
    adc_tmp112.config()?;

    i2c_mux_1.reset()?;
    i2c_mux_2.reset()?;

    Ok(())
}

pub fn read_drs_temp_raw() -> Result<u16, RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_1);
    i2c_mux.select(RB_DRS_TMP112_CHANNEL)?;
    let drs_tmp112 = tmp112::TMP112::new(I2C_BUS, RB_DRS_TMP112_ADDRESS);
    drs_tmp112.config()?;
    let drs_temp_raw = drs_tmp112.read_raw()?;

    i2c_mux.reset()?;

    Ok(drs_temp_raw)
}

pub fn to_json() -> Result<String, RBError> {
    let rb_temp = RBTemp::new();
    let rb_temp_json = serde_json::to_string(&rb_temp)?;

    Ok(rb_temp_json)
}