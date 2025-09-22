use crate::constant::*;
use crate::helper::pa_type::{PAReadBias, PASetBias, PATemp, PAError};
use crate::device::{max11615, max11617, max5825, pca9548a};
use crate::pb_control::pb_temp::read_pds_temp;

impl PAReadBias {
    pub fn new() -> Self {
        match Self::read_bias() {
            Ok(read_biases) => {
                read_biases
            }
            Err(_) => {
                Self {
                    read_biases: [f32::MAX; 16]
                }
            }
        }
    }
    pub fn read_bias() -> Result<PAReadBias, PAError> {
        let mut read_biases: [f32; 16] = Default::default();

        let preamp_channels = [
            PA_SEN_1_CHANNEL, PA_SEN_2_CHANNEL, PA_SEN_3_CHANNEL, PA_SEN_4_CHANNEL,
            PA_SEN_5_CHANNEL, PA_SEN_6_CHANNEL, PA_SEN_7_CHANNEL, PA_SEN_8_CHANNEL,
            PA_SEN_9_CHANNEL, PA_SEN_10_CHANNEL, PA_SEN_11_CHANNEL, PA_SEN_12_CHANNEL,
            PA_SEN_13_CHANNEL, PA_SEN_14_CHANNEL, PA_SEN_15_CHANNEL, PA_SEN_16_CHANNEL,
        ];
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
        i2c_mux.select(PB_ADC_1_CHANNEL)?;
        let max11615 = max11615::MAX11615::new(I2C_BUS, PB_MAX11615_ADDRESS);
        max11615.setup()?;
        let max11617 = max11617::MAX11617::new(I2C_BUS, PB_MAX11617_ADDRESS);
        max11617.setup()?;

        for i in 0..=7 {
            if (0..=3).contains(&i) {
                let preamp_bias_raw = max11615.read(preamp_channels[i])?;
                read_biases[i] = Self::convert_bias_voltage(preamp_bias_raw);
            } else {
                let preamp_bias_raw = max11617.read(preamp_channels[i])?;
                read_biases[i] = Self::convert_bias_voltage(preamp_bias_raw);
            }
        }

        i2c_mux.select(PB_ADC_2_CHANNEL)?;
        max11615.setup()?;
        max11617.setup()?;

        for i in 8..=15 {
            if (8..=11).contains(&i) {
                let preamp_bias_raw = max11615.read(preamp_channels[i])?;
                read_biases[i] = Self::convert_bias_voltage(preamp_bias_raw);
            } else {
                let preamp_bias_raw = max11617.read(preamp_channels[i])?;
                read_biases[i] = Self::convert_bias_voltage(preamp_bias_raw);
            }
        }

        i2c_mux.reset()?;

        Ok(
            PAReadBias {
                read_biases,
            }
        )
    }
    fn convert_bias_voltage(voltage: f32) -> f32 {
        // let bias_voltage = voltage * 22.27659574468085;
        let bias_voltage = voltage * (10f32.powi(6i32) + 47f32*10f32.powi(3i32))/(47f32*10f32.powi(3i32));

        bias_voltage
    }
}

impl PASetBias {
    pub fn read_set_bias() -> Result<Self, PAError> {

        let preamp_bias_channels = [
            PA_DAC_1_CHANNEL, PA_DAC_2_CHANNEL, PA_DAC_3_CHANNEL, PA_DAC_4_CHANNEL,
            PA_DAC_5_CHANNEL, PA_DAC_6_CHANNEL, PA_DAC_7_CHANNEL, PA_DAC_8_CHANNEL,
            PA_DAC_9_CHANNEL, PA_DAC_10_CHANNEL, PA_DAC_11_CHANNEL, PA_DAC_12_CHANNEL,
            PA_DAC_13_CHANNEL, PA_DAC_14_CHANNEL, PA_DAC_15_CHANNEL, PA_DAC_16_CHANNEL,
        ];
    
        let mut set_biases: [f32; 16] = Default::default();
    
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
    
        i2c_mux.select(PB_DAC_1_CHANNEL)?;
        let pb_dac_1 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        for i in 0..=7 {
            set_biases[i] = Self::adc_to_bias(pb_dac_1.read_dacn(preamp_bias_channels[i])?);
        }
    
        i2c_mux.select(PB_DAC_2_CHANNEL)?;
        let pb_dac_2 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        for i in 8..=15 {
            set_biases[i] = Self::adc_to_bias(pb_dac_2.read_dacn(preamp_bias_channels[i])?);
        }
    
        i2c_mux.reset()?;
    
        Ok(
            Self {
                set_biases
            }
        )
    }
    pub fn set_default_bias() -> Result<(), PAError> {

        let bias_voltage = Self::bias_to_adc(PA_DEFAULT_BIAS);
    
        let preamp_bias_channels = [
            PA_DAC_1_CHANNEL, PA_DAC_2_CHANNEL, PA_DAC_3_CHANNEL, PA_DAC_4_CHANNEL,
            PA_DAC_5_CHANNEL, PA_DAC_6_CHANNEL, PA_DAC_7_CHANNEL, PA_DAC_8_CHANNEL,
            PA_DAC_9_CHANNEL, PA_DAC_10_CHANNEL, PA_DAC_11_CHANNEL, PA_DAC_12_CHANNEL,
            PA_DAC_13_CHANNEL, PA_DAC_14_CHANNEL, PA_DAC_15_CHANNEL, PA_DAC_16_CHANNEL,
        ];
    
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
        
        i2c_mux.select(PB_DAC_1_CHANNEL)?;
        let pb_dac_1 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        for i in 0..=7 {
            pb_dac_1.coden_loadn(preamp_bias_channels[i], bias_voltage)?;
        }
    
        i2c_mux.select(PB_DAC_2_CHANNEL)?;
        let pb_dac_2 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        for i in 8..=15 {
            pb_dac_2.coden_loadn(preamp_bias_channels[i], bias_voltage)?;
        }
    
        i2c_mux.reset()?;
    
        Ok(())
    
    }
    pub fn set_manual_bias(channel: Option<u8>, bias: f32) -> Result<(), PAError> {

        if bias < 0.0 || bias > 67.0 {
            eprintln!("Bias voltage must be between 0V to 67V");
            std::process::exit(1);
        }

        let bias_voltage = Self::bias_to_adc(bias);

        let preamp_bias_channels = [
            PA_DAC_1_CHANNEL, PA_DAC_2_CHANNEL, PA_DAC_3_CHANNEL, PA_DAC_4_CHANNEL,
            PA_DAC_5_CHANNEL, PA_DAC_6_CHANNEL, PA_DAC_7_CHANNEL, PA_DAC_8_CHANNEL,
            PA_DAC_9_CHANNEL, PA_DAC_10_CHANNEL, PA_DAC_11_CHANNEL, PA_DAC_12_CHANNEL,
            PA_DAC_13_CHANNEL, PA_DAC_14_CHANNEL, PA_DAC_15_CHANNEL, PA_DAC_16_CHANNEL,
        ];

        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
        match channel {
            None => {
                i2c_mux.select(PB_DAC_1_CHANNEL)?;
                let pb_dac_1 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
                for i in 0..=7 {
                    pb_dac_1.coden_loadn(preamp_bias_channels[i], bias_voltage)?;
                }
            
                i2c_mux.select(PB_DAC_2_CHANNEL)?;
                let pb_dac_2 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
                for i in 8..=15 {
                    pb_dac_2.coden_loadn(preamp_bias_channels[i], bias_voltage)?;
                }
            }
            Some(mut ch) => {

                if ch < 1 || ch > 16 {
                    eprintln!("Channel must be between 1 to 16.");
                    std::process::exit(1);
                }

                ch = ch - 1;

                if (0..=7).contains(&ch) {
                    i2c_mux.select(PB_DAC_1_CHANNEL)?;
                    let pb_dac_1 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
                    pb_dac_1.coden_loadn(preamp_bias_channels[ch as usize], bias_voltage)?;
                } else {
                    i2c_mux.select(PB_DAC_2_CHANNEL)?;
                    let pb_dac_2 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
                    pb_dac_2.coden_loadn(preamp_bias_channels[ch as usize], bias_voltage)?
                }
            }
        }
    
        i2c_mux.reset()?;
    
        Ok(())
    }
    pub fn set_manual_biases(biases: [f32; 16]) -> Result<(), PAError> {
        
        for bias in biases {
            if bias < 0.0 || bias > 67.0 {
                eprintln!("Bias voltage must be between 0V to 67V");
                std::process::exit(1);
            }
        }

        let preamp_bias_channels = [
            PA_DAC_1_CHANNEL, PA_DAC_2_CHANNEL, PA_DAC_3_CHANNEL, PA_DAC_4_CHANNEL,
            PA_DAC_5_CHANNEL, PA_DAC_6_CHANNEL, PA_DAC_7_CHANNEL, PA_DAC_8_CHANNEL,
            PA_DAC_9_CHANNEL, PA_DAC_10_CHANNEL, PA_DAC_11_CHANNEL, PA_DAC_12_CHANNEL,
            PA_DAC_13_CHANNEL, PA_DAC_14_CHANNEL, PA_DAC_15_CHANNEL, PA_DAC_16_CHANNEL,
        ];

        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);

        i2c_mux.select(PB_DAC_1_CHANNEL)?;
        let pb_dac_1 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        for i in 0..=7 {
            pb_dac_1.coden_loadn(preamp_bias_channels[i], Self::bias_to_adc(biases[i]))?;
        }
    
        i2c_mux.select(PB_DAC_2_CHANNEL)?;
        let pb_dac_2 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        for i in 8..=15 {
            pb_dac_2.coden_loadn(preamp_bias_channels[i], Self::bias_to_adc(biases[i]))?;
        }
    
        i2c_mux.reset()?;

        Ok(())
    }
    pub fn set_bias() -> Result<(), PAError> {

        // let mut bias_voltage = Default::default();
    
        let preamp_bias_channels = [
            PA_DAC_1_CHANNEL, PA_DAC_2_CHANNEL, PA_DAC_3_CHANNEL, PA_DAC_4_CHANNEL,
            PA_DAC_5_CHANNEL, PA_DAC_6_CHANNEL, PA_DAC_7_CHANNEL, PA_DAC_8_CHANNEL,
            PA_DAC_9_CHANNEL, PA_DAC_10_CHANNEL, PA_DAC_11_CHANNEL, PA_DAC_12_CHANNEL,
            PA_DAC_13_CHANNEL, PA_DAC_14_CHANNEL, PA_DAC_15_CHANNEL, PA_DAC_16_CHANNEL,
        ];
    
        let mut bias_voltages: [u16; 16] = Default::default();

        let read_biases = PAReadBias::read_bias()?.read_biases;
        let set_biases = Self::read_set_bias()?.set_biases;
    
        for i in 0..=15 {
            if set_biases[i] == 0.0 {
                let bias_stc = Self::sipm_temp_comp(i)?;
                let bias_ptc = Self::pb_temp_comp(bias_stc)?;

                bias_voltages[i] = Self::bias_to_adc(bias_ptc);
                // if [0, 3, 7, 8, 11, 14].contains(&i) {
                //     println!("Preamp {} Case 1: {}", i+1, bias_ptc);
                // }
            } else {
                let delta = (read_biases[i] - set_biases[i]).abs();
                if delta > 0.1 {
                    if read_biases[i] > set_biases[i] {
                        bias_voltages[i] = Self::bias_to_adc(set_biases[i] + delta);
                        // if [0, 3, 7, 8, 11, 14].contains(&i) {
                        //     println!("Preamp {} Case 2: {}", i+1, set_biases[i] + delta);
                        // }
                    } else if read_biases[i] < set_biases[i] {
                        bias_voltages[i] = Self::bias_to_adc(set_biases[i] - delta);
                        // if [0, 3, 7, 8, 11, 14].contains(&i) {
                        //     println!("Preamp {} Case 3: {}", i+1, set_biases[i] + delta);
                        // }
                    } else {
                        bias_voltages[i] = Self::bias_to_adc(set_biases[i]);
                        // if [0, 3, 7, 8, 11, 14].contains(&i)  {
                        //     println!("Preamp {} Case 4: {}", i+1, set_biases[i]);
                        // }
                    }
                } else {
                    let bias_stc = Self::sipm_temp_comp(i)?;
                    let bias_ptc = Self::pb_temp_comp(bias_stc)?;
                    
                    bias_voltages[i] = Self::bias_to_adc(bias_ptc);
                    // if [0, 3, 7, 8, 11, 14].contains(&i)  {
                    //     println!("Preamp {} Case 5: {}", i+1, bias_ptc);
                    // }
                }
            }
        }
    
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
        
        i2c_mux.select(PB_DAC_1_CHANNEL)?;
        let pb_dac_1 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        for i in 0..=7 {
            pb_dac_1.coden_loadn(preamp_bias_channels[i], bias_voltages[i])?;
        }
    
        i2c_mux.select(PB_DAC_2_CHANNEL)?;
        let pb_dac_2 = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        for i in 8..=15 {
            pb_dac_2.coden_loadn(preamp_bias_channels[i], bias_voltages[i])?;
        }
    
        i2c_mux.reset()?;
    
        Ok(())
    }
    pub fn sipm_temp_comp(ch: usize) -> Result<f32, PAError> {
        let bias_voltage;
        
        let preamp_temp = PATemp::read_signle_temp(ch)?;
        if preamp_temp == f32::MAX {
            bias_voltage = 0.0
        } else {
            if (0..=15).contains(&ch) {
                bias_voltage = PA_DEFAULT_BIAS + (preamp_temp - 20.0) * 0.054;
            } else {
                bias_voltage = 0.0;
            }
        }
        // if (0..=15).contains(&ch) {
        //     bias_voltage = PREAMP_DEFAULT_BIAS + (preamp_temp - 20.0) * 0.054;
        // } else {
        //     bias_voltage = 0.0;
        // }

        Ok(bias_voltage)
    }
    pub fn pb_temp_comp(bias_stc: f32) -> Result<f32, PAError> {
        let pb_temp = read_pds_temp()?;

        let bias_voltage = bias_stc - 0.2 + 0.005 * pb_temp + 4.0 * 10f32.powi(-5) * pb_temp.powi(2);

        Ok(bias_voltage)
    }
    pub fn reset_bias() -> Result<(), PAError> {
        let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, PB_PCA9548A_ADDRESS);
    
        i2c_mux.select(PB_DAC_1_CHANNEL)?;
        let pb_dac = max5825::MAX5825::new(I2C_BUS, PB_MAX5825_ADDRESS);
        pb_dac.reset_dac()?;
        i2c_mux.select(PB_DAC_2_CHANNEL)?;
        pb_dac.reset_dac()?;
    
        i2c_mux.reset()?;
    
        Ok(())
    
    }
    fn bias_to_adc(bias_voltage: f32) -> u16 {
        let adc = (bias_voltage / 22.3) / PB_DAC_REF_VOLTAGE * 2f32.powi(12);
    
        adc as u16
    }
    fn adc_to_bias(adc: u16) -> f32 {
        let bias_voltage = adc as f32 * PB_DAC_REF_VOLTAGE * 22.3 * 2f32.powi(-12);
    
        bias_voltage
    }
    
}