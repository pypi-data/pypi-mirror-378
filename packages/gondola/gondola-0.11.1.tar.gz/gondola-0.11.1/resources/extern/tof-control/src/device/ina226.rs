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
const CONFIG_RST: u16 = 0xC000;
const CONFIG_AVG_1: u16 = 0x4000;
const CONFIG_AVG_4: u16 = 0x4200;
const CONFIG_AVG_16: u16 = 0x4400;
const CONFIG_AVG_64: u16 = 0x4600;
const CONFIG_AVG_128: u16 = 0x4800;
const CONFIG_AVG_256: u16 = 0x4A00;
const CONFIG_AVG_512: u16 = 0x4C00;
const CONFIG_AVG_1024: u16 = 0x4E00;
const CONFIG_VBUSCT_140: u16 = 0x4000;
const CONFIG_VBUSCT_204: u16 = 0x4040;
const CONFIG_VBUSCT_332: u16 = 0x4080;
const CONFIG_VBUSCT_588: u16 = 0x40C0;
const CONFIG_VBUSCT_1100: u16 = 0x4100;
const CONFIG_VBUSCT_2116: u16 = 0x4140;
const CONFIG_VBUSCT_4156: u16 = 0x4180;
const CONFIG_VBUSCT_8244: u16 = 0x41C0;
const CONFIG_VSHCT_140: u16 = 0x4000;
const CONFIG_VSHCT_204: u16 = 0x4008;
const CONFIG_VSHCT_332: u16 = 0x4010;
const CONFIG_VSHCT_588: u16 = 0x4018;
const CONFIG_VSHCT_1100: u16 = 0x4020;
const CONFIG_VSHCT_2116: u16 = 0x4028;
const CONFIG_VSHCT_4156: u16 = 0x4030;
const CONFIG_VSHCT_8244: u16 = 0x4038;
const CONFIG_MODE_PDS: u16 = 0x4000; // Power-Down (or Shutdown)
const CONFIG_MODE_SVT: u16 = 0x4001; // Shunt Voltage, Triggered
const CONFIG_MODE_BVT: u16 = 0x4002; // Bus Voltage, Triggered
const CONFIG_MODE_SBT: u16 = 0x4003; // Shunt and Bus, Triggered
const CONFIG_MODE_PDS_2: u16 = 0x4004; // Power-Down (or Shutdown) 2
const CONFIG_MODE_SVC: u16 = 0x4005; // Shunt Voltage, Continuous
const CONFIG_MODE_BVC: u16 = 0x4006; // Bus Voltage, Continuous
const CONFIG_MODE_SBC: u16 = 0x4007; // Shunt and Bus, Continuous

pub struct INA226 {
    bus: u8,
    address: u16,
    rshunt: f32, // shunt resistance value
    mec: f32,    // maximum expected current
}

impl INA226 {
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

        let config = CONFIG_AVG_16 | CONFIG_VBUSCT_332 | CONFIG_VSHCT_332 | CONFIG_MODE_SBT;
        dev.smbus_write_i2c_block_data(CONFIG as u8, &config.to_be_bytes())
    }
    fn calibrate(&self, dev: &mut LinuxI2CDevice) -> Result<[f32; 2], LinuxI2CError> {
        let c_lsb = self.mec / 2f32.powf(15.0);
        let p_lsb = 25.0 * c_lsb;
        let cal = 0.00512 / (c_lsb * self.rshunt);

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

        let shunt_voltage = sign * (shunt_voltage_adc as f32) * 0.0000025;

        Ok(shunt_voltage)
    }
    fn read_bus_voltage(&self, dev: &mut LinuxI2CDevice) -> Result<f32, LinuxI2CError> {
        let bus_voltage_raw = dev.smbus_read_i2c_block_data(BUS as u8, 2)?;
        let bus_voltage_adc = ((bus_voltage_raw[0] as u16) << 8) | (bus_voltage_raw[1] as u16);
        let bus_voltage = (bus_voltage_adc as f32) * 0.00125;

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
