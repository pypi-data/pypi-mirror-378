use crate::constant::*;
use crate::helper::ltb_type::{LTBThreshold, LTBError};
use crate::device::max5815;

impl LTBThreshold {
    pub fn new() -> Self {
        match Self::read_thresholds() {
            Ok(thresholds) => {
                thresholds
            }
            Err(_) => {
                Self {
                    thresh_0: f32::MAX,
                    thresh_1: f32::MAX,
                    thresh_2: f32::MAX,
                }
            }
        }

    }
    pub fn read_threshold(channel: u8) -> Result<f32, LTBError> {
        let ltb_dac = max5815::MAX5815::new(I2C_BUS, LTB_MAX5815_ADDRESS);
        let threshold_raw = ltb_dac.read_dacn(channel)?;
        let threshold = Self::adc_to_mv(threshold_raw);

        Ok(threshold)
    }
    pub fn read_thresholds() -> Result<LTBThreshold, LTBError> {
        let ltb_dac: max5815::MAX5815 = max5815::MAX5815::new(I2C_BUS, LTB_MAX5815_ADDRESS);
        let mut thresholds: [f32; 3] = Default::default();
        for i in 0..=2 {
            let threshold_raw = ltb_dac.read_dacn(i)?;
            thresholds[i as usize] = Self::adc_to_mv(threshold_raw);
        }

        Ok(
            LTBThreshold {
                thresh_0: thresholds[0],
                thresh_1: thresholds[1],
                thresh_2: thresholds[2],
            }
        )
    }
    fn adc_to_mv(adc: u16) -> f32 {
        let voltage = LTB_DAC_REF_VOLTAGE * (adc as f32) / 2f32.powf(12.0);

        voltage * 1000.0
    }
}

pub fn set_default_threshold() -> Result<(), LTBError> {
    let ltb_dac = max5815::MAX5815::new(I2C_BUS, LTB_MAX5815_ADDRESS);
    ltb_dac.configure()?;

    let default_thresholds = [LTB_DAC_THRESHOLD_0, LTB_DAC_THRESHOLD_1, LTB_DAC_THRESHOLD_2];

    for (i, default_threshold) in default_thresholds.iter().enumerate() {
        ltb_dac.coden_loadn(i as u8, mv_to_adc(*default_threshold))?;
    };

    Ok(())
}

pub fn set_threshold(channel: u8, threshold: f32) -> Result<(), LTBError> {

    if !(0..=2).contains(&channel) {
        return Err(LTBError::SetThreshold)
    } 

    let ltb_dac = max5815::MAX5815::new(I2C_BUS, LTB_MAX5815_ADDRESS);
    ltb_dac.configure()?;

    ltb_dac.coden_loadn(channel, mv_to_adc(threshold))?;

    Ok(())
}

pub fn set_thresholds(thresholds: [f32; 3]) -> Result<(), LTBError> {

    let ltb_dac = max5815::MAX5815::new(I2C_BUS, LTB_MAX5815_ADDRESS);
    ltb_dac.configure()?;

    for (i, threshold) in thresholds.iter().enumerate() {

        if (*threshold < 0.0) | (*threshold > 1000.0) {
            return Err(LTBError::SetThreshold)
        }
        
        ltb_dac.coden_loadn(i as u8, mv_to_adc(*threshold))?;
    }

    Ok(())
}

fn mv_to_adc(mv: f32) -> u16 {
let adc = (mv / 1000.0) / LTB_DAC_REF_VOLTAGE * 2f32.powf(12.0);

adc as u16
}

pub fn reset_threshold() -> Result<(), LTBError> {
    let ltb_dac = max5815::MAX5815::new(I2C_BUS, LTB_MAX5815_ADDRESS);
    ltb_dac.reset_dac()?;

    Ok(())
}