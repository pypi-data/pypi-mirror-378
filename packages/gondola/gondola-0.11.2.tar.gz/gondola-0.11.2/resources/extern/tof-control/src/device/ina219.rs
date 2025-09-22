#![allow(unused)]
use crate::constant::*;

use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// Register
const CONFIG: u16 = 0x00;
const SHUNT: u16 = 0x01;
const BUS: u16 = 0x02;
const POWER: u16 = 0x03;
const CURRENT: u16 = 0x04;
const CALIB: u16 = 0x05;
// Configuration Parameters
const CONFIG_RST: u16 = 0x8000;
const CONFIG_BRNG_16: u16 = 0x0000;
const CONFIG_BRNG_32: u16 = 0x2000;
const CONFIG_PG_40: u16 = 0x0000;
const CONFIG_PG_80: u16 = 0x0800;
const CONFIG_PG_160: u16 = 0x1000;
const CONFIG_PG_320: u16 = 0x1800;
const CONFIG_BADC_9B: u16 = 0x0000;
const CONFIG_BADC_10B: u16 = 0x0080;
const CONFIG_BADC_11B: u16 = 0x0100;
const CONFIG_BADC_12B_D: u16 = 0x0180;
const CONFIG_BADC_12B: u16 = 0x0400;
const CONFIG_BADC_2S: u16 = 0x0480;
const CONFIG_BADC_4S: u16 = 0x0500;
const CONFIG_BADC_8S: u16 = 0x0580;
const CONFIG_BADC_16S: u16 = 0x0600;
const CONFIG_BADC_32S: u16 = 0x0680;
const CONFIG_BADC_64S: u16 = 0x0700;
const CONFIG_BADC_128S: u16 = 0x0780;
const CONFIG_SADC_9B: u16 = 0x0000;
const CONFIG_SADC_10B: u16 = 0x0008;
const CONFIG_SADC_11B: u16 = 0x0010;
const CONFIG_SADC_12B_D: u16 = 0x0018;
const CONFIG_SADC_12B: u16 = 0x0040;
const CONFIG_SADC_2S: u16 = 0x0048;
const CONFIG_SADC_4S: u16 = 0x0050;
const CONFIG_SADC_8S: u16 = 0x0058;
const CONFIG_SADC_16S: u16 = 0x0060;
const CONFIG_SADC_32S: u16 = 0x0068;
const CONFIG_SADC_64S: u16 = 0x0070;
const CONFIG_SADC_128S: u16 = 0x0078;
const CONFIG_MODE_PD: u16 = 0x0000; // Power-Down
const CONFIG_MODE_SVT: u16 = 0x0001; // Shunt Voltage, Triggered
const CONFIG_MODE_BVT: u16 = 0x0002; // Bus Voltage, Triggered
const CONFIG_MODE_SBT: u16 = 0x0003; // Shunt and Bus, Triggered
const CONFIG_MODE_ADO: u16 = 0x0004; // ADC off (disabled)
const CONFIG_MODE_SVC: u16 = 0x0005; // Shunt Voltage, Continuous
const CONFIG_MODE_BVC: u16 = 0x0006; // Bus Voltage, Continuous
const CONFIG_MODE_SBC: u16 = 0x0007; // Shunt and Bus, Continuous

pub struct INA219 {
    bus: u8,
    address: u16,
    rshunt: f32, // shunt resistance value
    mec: f32,    // maximum expected current
}

impl INA219 {
    pub fn new(bus: u8, address: u16, rshunt: f32, mec: f32) -> Self {
        Self {
            bus,
            address,
            rshunt,
            mec,
        }
    }
    pub fn configure(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        let config =
            CONFIG_BRNG_32 | CONFIG_PG_320 | CONFIG_BADC_16S | CONFIG_SADC_16S | CONFIG_MODE_SBT;
        dev.smbus_write_i2c_block_data(CONFIG as u8, &config.to_be_bytes())
    }
    fn calibrate(&self, dev: &mut LinuxI2CDevice) -> Result<[f32; 2], LinuxI2CError> {
        let c_lsb = self.mec / 2f32.powf(15.0);
        let p_lsb = 20.0 * c_lsb;
        let cal = 0.04096 / (c_lsb * self.rshunt);

        dev.smbus_write_i2c_block_data(CALIB as u8, &(cal as u16).to_be_bytes())?;

        let cal_lsb = [c_lsb, p_lsb];

        Ok(cal_lsb)
    }
    pub fn read(&self) -> Result<[f32; 3], LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        let shunt_voltage = self.read_shunt_voltage(&mut dev)?;
        let bus_voltage = self.read_bus_voltage(&mut dev)?;

        let cal_lsb = self.calibrate(&mut dev)?;

        let current = self.read_current(&mut dev, cal_lsb[0])?;
        let power = self.read_power(&mut dev, cal_lsb[1])?;

        let vcp = [bus_voltage, current, power];

        Ok(vcp)
    }
    fn read_shunt_voltage(&self, dev: &mut LinuxI2CDevice) -> Result<f32, LinuxI2CError> {
        let shunt_voltage_raw = dev.smbus_read_i2c_block_data(SHUNT as u8, 2)?;
        let mut shunt_voltage_adc =
            ((shunt_voltage_raw[0] as u16) << 8) | (shunt_voltage_raw[1] as u16);
        let mut sign: f32 = 1.0;
        if shunt_voltage_adc >= 0x8000 {
            sign = -1.0;
            shunt_voltage_adc = (shunt_voltage_adc & 0x7FFF) + 1;
        }

        let shunt_voltage = sign * (shunt_voltage_adc as f32) * 0.00001;

        Ok(shunt_voltage)
    }
    fn read_bus_voltage(&self, dev: &mut LinuxI2CDevice) -> Result<f32, LinuxI2CError> {
        let bus_voltage_raw = dev.smbus_read_i2c_block_data(BUS as u8, 2)?;
        let bus_voltage_adc =
            (((bus_voltage_raw[0] as u16) << 8) | (bus_voltage_raw[1] as u16)) >> 3 & 0x1FFF;
        let bus_voltage = (bus_voltage_adc as f32) * 0.004;

        Ok(bus_voltage)
    }
    fn read_current(&self, dev: &mut LinuxI2CDevice, c_lsb: f32) -> Result<f32, LinuxI2CError> {
        let mut current_raw = dev.smbus_read_i2c_block_data(CURRENT as u8, 2)?;
        let mut current_adc = ((current_raw[0] as u16) << 8) | (current_raw[1] as u16);
        // while current_adc == 0 {
        //     current_raw = dev.smbus_read_i2c_block_data(CURRENT as u8, 2)?;
        //     current_adc = ((current_raw[0] as u16) << 8) | (current_raw[1] as u16);
        // }
        let mut sign: f32 = 1.0;
        if current_adc >= 0x8000 {
            sign = -1.0;
            current_adc = (current_adc & 0x7FFF) + 1;
        }

        let current = sign * (current_adc as f32) * c_lsb;

        Ok(current)
    }
    fn read_power(&self, dev: &mut LinuxI2CDevice, p_lsb: f32) -> Result<f32, LinuxI2CError> {
        let mut power_raw = dev.smbus_read_i2c_block_data(POWER as u8, 2)?;
        let mut power_adc = ((power_raw[0] as u16) << 8) | (power_raw[1] as u16);
        // while power_adc == 0 {
        //     power_raw = dev.smbus_read_i2c_block_data(POWER as u8, 2)?;
        //     power_adc = ((power_raw[0] as u16) << 8) | (power_raw[1] as u16);
        // }
        let power = (power_adc as f32) * p_lsb;

        Ok(power)
    }
    fn reset(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        dev.smbus_write_i2c_block_data(CONFIG as u8, &CONFIG_RST.to_be_bytes())
    }
}
