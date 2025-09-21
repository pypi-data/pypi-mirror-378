#![allow(unused)]
use crate::constant::*;

use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// BME280 Register
const ID: u16 = 0xD0;
const RESET: u16 = 0xE0;
const RESET_CODE: u16 = 0xB6;
const CONFIG: u16 = 0xF5;
const CTRL_HUM: u16 = 0xF2;
const STATUS: u16 = 0xF3;
const CTRL_MEAS: u16 = 0xF4;
const HUM_LSB: u16 = 0xFE;
const HUM_MSB: u16 = 0xFD;
const TEMP_XLSB: u16 = 0xFC;
const TEMP_LSB: u16 = 0xFB;
const TEMP_MSB: u16 = 0xFA;
const PRESS_XLSB: u16 = 0xF9;
const PRESS_LSB: u16 = 0xF8;
const PRESS_MSB: u16 = 0xF7;
const TEMP_COMP: u16 = 0x88;
const PRESS_COMP: u16 = 0x8E;
const HUM_COMP_1: u16 = 0xA1;
const HUM_COMP_2: u16 = 0xE1;
// BME280 Configuration Register
const T_SB_0_5: u16 = 0x00; // T standby 0.5ms
const T_SB_62_5: u16 = 0x20; // T standby 62.5ms
const T_SB_125: u16 = 0x40; // T standby 125ms
const T_SB_250: u16 = 0x60; // T standby 250ms
const T_SB_500: u16 = 0x80; // T standby 500ms
const T_SB_1000: u16 = 0xA0; // T standby 1000ms
const T_SB_10: u16 = 0xC0; // T standby 10ms
const T_SB_20: u16 = 0xE0; // T standby 20ms
const FILTER_OFF: u16 = 0x00; // Filter off
const FILTER_2: u16 = 0x04; // Filter coefficient 2
const FILTER_4: u16 = 0x08; // Filter coefficient 4
const FILTER_8: u16 = 0x0C; // Filter coefficient 8
const FILTER_16: u16 = 0x10; // Filter coefficient 16
const SPI3W_DI: u16 = 0x00; // SPI interface disabled
const SPI3W_EN: u16 = 0x01; // SPI interface enabled
                            // BME280 Humidity Control Register
const OSRS_H_S: u16 = 0x00; // Oversampling skipped
const OSRS_H_1: u16 = 0x01; // Oversampling x1
const OSRS_H_2: u16 = 0x02; // Oversampling x2
const OSRS_H_4: u16 = 0x03; // Oversampling x4
const OSRS_H_8: u16 = 0x04; // Oversampling x8
const OSRS_H_16: u16 = 0x05; // Oversampling x16
                             // BME280 Temperature and Pressure Control Register
const OSRS_T_S: u16 = 0x00; // Oversampling skipped
const OSRS_T_1: u16 = 0x20; // Oversampling x1
const OSRS_T_2: u16 = 0x40; // Oversampling x2
const OSRS_T_4: u16 = 0x60; // Oversampling x4
const OSRS_T_8: u16 = 0x80; // Oversampling x8
const OSRS_T_16: u16 = 0xA0; // Oversampling x16
const OSRS_P_S: u16 = 0x00; // Oversampling skipped
const OSRS_P_1: u16 = 0x04; // Oversampling x1
const OSRS_P_2: u16 = 0x08; // Oversampling x2
const OSRS_P_4: u16 = 0x0C; // Oversampling x4
const OSRS_P_8: u16 = 0x10; // Oversampling x8
const OSRS_P_16: u16 = 0x14; // Oversampling x16
const MODE_S: u16 = 0x00; // Sleep mode
const MODE_F: u16 = 0x01; // Forced mode
const MODE_N: u16 = 0x03; // Normal mode

pub struct BME280 {
    bus: u8,
    address: u16,
}
struct CompensateData {
    dig_t: Vec<u16>,
    dig_p: Vec<u16>,
    dig_h: Vec<u16>,
}

impl BME280 {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn configure(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        self.ctrl_humidity(&mut dev)?;
        self.ctrl_measurement(&mut dev)?;

        let config = T_SB_250 | FILTER_OFF | SPI3W_DI;
        dev.smbus_write_byte_data(CONFIG as u8, config as u8)?;

        Ok(())
    }
    fn ctrl_humidity(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        dev.smbus_write_byte_data(CTRL_HUM as u8, OSRS_H_1 as u8)?;

        Ok(())
    }
    fn ctrl_measurement(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        let config = OSRS_T_1 | OSRS_P_1 | MODE_N;
        dev.smbus_write_byte_data(CTRL_MEAS as u8, config as u8)?;

        Ok(())
    }
    fn reset(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        dev.smbus_write_byte_data(RESET as u8, RESET_CODE as u8)?;

        Ok(())
    }
    fn read_compensate(&self, dev: &mut LinuxI2CDevice) -> Result<CompensateData, LinuxI2CError> {
        let mut dig_t = Vec::new();
        let mut dig_p = Vec::new();
        let mut dig_h = Vec::new();

        let dat_t = dev.smbus_read_i2c_block_data(TEMP_COMP as u8, 6)?;
        dig_t.push(((dat_t[1] as u16) << 8) | (dat_t[0] as u16));
        dig_t.push(((dat_t[3] as u16) << 8) | (dat_t[2] as u16));
        dig_t.push(((dat_t[5] as u16) << 8) | (dat_t[4] as u16));
        for i in 1..3 {
            if dig_t[i] >= 0x8000 {
                dig_t[i] = 0xFFFF - dig_t[i];
            }
        }

        let dat_p = dev.smbus_read_i2c_block_data(PRESS_COMP as u8, 18)?;
        dig_p.push(((dat_p[1] as u16) << 8) | (dat_p[0] as u16));
        dig_p.push(((dat_p[3] as u16) << 8) | (dat_p[2] as u16));
        dig_p.push(((dat_p[5] as u16) << 8) | (dat_p[4] as u16));
        dig_p.push(((dat_p[7] as u16) << 8) | (dat_p[6] as u16));
        dig_p.push(((dat_p[9] as u16) << 8) | (dat_p[8] as u16));
        dig_p.push(((dat_p[11] as u16) << 8) | (dat_p[10] as u16));
        dig_p.push(((dat_p[13] as u16) << 8) | (dat_p[12] as u16));
        dig_p.push(((dat_p[15] as u16) << 8) | (dat_p[14] as u16));
        dig_p.push(((dat_p[17] as u16) << 8) | (dat_p[16] as u16));
        for i in 1..9 {
            if dig_p[i] >= 0x8000 {
                dig_p[i] = 0xFFFF - dig_p[i];
            }
        }

        let dh = dev.smbus_read_byte_data(HUM_COMP_1 as u8)?;
        dig_h.push(dh as u16);
        let dat_h = dev.smbus_read_i2c_block_data(HUM_COMP_2 as u8, 8)?;
        dig_h.push(((dat_h[1] as u16) << 8) | (dat_h[0] as u16));
        dig_h.push(dat_h[2] as u16);
        dig_h.push(((dat_h[3] as u16) << 4) | 0x0F & (dat_h[4] as u16));
        dig_h.push(((dat_h[5] as u16) << 4) | (((dat_h[4] as u16) >> 4) & 0x0F));
        dig_h.push(dat_h[6] as u16);
        if dig_h[1] >= 0x8000 {
            dig_h[1] = 0xFFFF - dig_h[1];
        };
        for i in 3..5 {
            if dig_h[i] >= 0x800 {
                dig_h[i] = 0xFFF - dig_h[i];
            }
        }
        if dig_h[5] >= 0x80 {
            dig_h[5] = 0xFF - dig_h[5];
        };

        Ok(
            CompensateData {
                dig_t,
                dig_p,
                dig_h,
            }
        )
    }
    pub fn read(&self) -> Result<[f32; 2], LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        let compensate_data = self.read_compensate(&mut dev)?;

        let temp_measurement = self.read_temperature(&mut dev, compensate_data.dig_t)?;
        let _temperature = temp_measurement[0];
        let t_fine = temp_measurement[1];

        let pressure = self
            .read_pressure(&mut dev, t_fine, compensate_data.dig_p)
            .expect("cannot read pressure from BME280");

        let humidity = self
            .read_humidity(&mut dev, t_fine, compensate_data.dig_h)
            .expect("cannot read humidity from BME280");

        let ph = [pressure, humidity];

        Ok(ph)
    }
    pub fn read_all(&self) -> Result<[f32; 3], LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        let compensate_data = self.read_compensate(&mut dev)?;

        let temp_measurement = self.read_temperature(&mut dev, compensate_data.dig_t)?;
        let temperature = temp_measurement[0];
        let t_fine = temp_measurement[1];

        let pressure = self
            .read_pressure(&mut dev, t_fine, compensate_data.dig_p)
            .expect("cannot read pressure from BME280");

        let humidity = self
            .read_humidity(&mut dev, t_fine, compensate_data.dig_h)
            .expect("cannot read humidity from BME280");

        let tph = [temperature, pressure, humidity];

        Ok(tph)
    }
    fn read_temperature(
        &self,
        dev: &mut LinuxI2CDevice,
        dig_t: Vec<u16>,
    ) -> Result<[f32; 2], LinuxI2CError> {
        let temp_msb = dev.smbus_read_byte_data(TEMP_MSB as u8)?;
        let temp_lsb = dev.smbus_read_byte_data(TEMP_LSB as u8)?;
        let temp_xlsb = dev.smbus_read_byte_data(TEMP_XLSB as u8)?;

        let temp_adc =
            ((temp_msb as u32) << 12) | ((temp_lsb as u32) << 4) | ((temp_xlsb as u32) >> 4);
        let temp_result = self.compensate_temperature(temp_adc, dig_t);
        let temp = temp_result[0];
        let t_fine = temp_result[1];

        Ok([temp, t_fine])
    }
    fn compensate_temperature(&self, adc: u32, dig_t: Vec<u16>) -> [f32; 2] {
        let var1 = ((adc as f32) / 8.0 - (dig_t[0] as f32) * 2.0) * (dig_t[1] as f32) / 2048.0;
        let var2 = ((adc as f32) / 16.0 - (dig_t[0] as f32))
            * ((adc as f32) / 16.0 - (dig_t[0] as f32))
            / 4096.0
            * (dig_t[2] as f32)
            / 16384.0;
        let t_fine = var1 + var2;

        let temp = ((t_fine * 5.0 + 128.0) / 256.0) / 100.0;

        [temp, t_fine]
    }
    fn read_pressure(
        &self,
        dev: &mut LinuxI2CDevice,
        t_fine: f32,
        dig_p: Vec<u16>,
    ) -> Result<f32, LinuxI2CError> {
        let press_msb = dev.smbus_read_byte_data(PRESS_MSB as u8)?;
        let press_lsb = dev.smbus_read_byte_data(PRESS_LSB as u8)?;
        let press_xlsb = dev.smbus_read_byte_data(PRESS_XLSB as u8)?;

        let press_adc =
            ((press_msb as u32) << 12) | ((press_lsb as u32) << 4) | ((press_xlsb as u32) >> 4);
        let press = self.compensate_pressure(t_fine, press_adc, dig_p);

        Ok(press)
    }
    fn compensate_pressure(&self, t_fine: f32, adc: u32, dig_p: Vec<u16>) -> f32 {
        let mut var1 = t_fine - 128000.0;
        let mut var2 = var1 * var1 * (dig_p[5] as f32);
        var2 = var2 + ((var1 * (dig_p[4] as f32)) * 131072.0);
        var2 = var2 + ((dig_p[3] as f32) * 34359738370.0);
        var1 = ((var1 * var1 * (dig_p[2] as f32)) / 256.0) + (var1 * (dig_p[1] as f32)) * 4096.0;
        var1 = (140737488400000.0 + var1) * ((dig_p[0] as f32) / 8589934592.0);

        if var1 == 0.0 {
            return 0.0;
        }

        let mut p = 1048576.0 - (adc as f32);
        p = ((p * 2147483648.0 - var2) * 3125.0) / var1;

        var1 = ((dig_p[8] as f32) * (p / 8192.0) * (p / 8192.0)) / 33554432.0;
        var2 = ((dig_p[7] as f32) * p) / 524288.0;

        p = (p + var1 + var2) / 256.0 + (dig_p[6] as f32) * 16.0;
        p = p / 256.0 / 100.0;

        p
    }
    fn read_humidity(
        &self,
        dev: &mut LinuxI2CDevice,
        t_fine: f32,
        dig_h: Vec<u16>,
    ) -> Result<f32, LinuxI2CError> {
        let hum_msb = dev.smbus_read_byte_data(HUM_MSB as u8)?;
        let hum_lsb = dev.smbus_read_byte_data(HUM_LSB as u8)?;

        let hum_adc = ((hum_msb as u16) << 8) | (hum_lsb as u16);
        let humidity = self.compensate_humidity(t_fine, hum_adc, dig_h);

        Ok(humidity)
    }
    fn compensate_humidity(&self, t_fine: f32, adc: u16, dig_h: Vec<u16>) -> f32 {
        let mut var_h = t_fine - 76800.0;
        var_h = ((adc as f32) - ((dig_h[3] as f32) * 64.0 + (dig_h[4] as f32) / 16384.0 * var_h))
            * ((dig_h[1] as f32) / 65536.0
                * (1.0
                    + (dig_h[5] as f32) / 67108864.0
                        * var_h
                        * (1.0 + (dig_h[2] as f32) / 67108864.0 * var_h)));
        var_h = var_h * (1.0 - (dig_h[0] as f32) * var_h / 524288.0);

        var_h
    }
}
