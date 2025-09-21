#![allow(unused)]
use crate::constant::*;

use i2cdev::core::*;
use i2cdev::linux::{LinuxI2CDevice, LinuxI2CError};

// LIS3MDLTR Register
const WHO_AM_I: u16 = 0x0F;
const CTRL_REG1: u16 = 0x20;
const CTRL_REG2: u16 = 0x21;
const CTRL_REG3: u16 = 0x22;
const CTRL_REG4: u16 = 0x23;
const CTRL_REG5: u16 = 0x24;
const STATUS: u16 = 0x27;
const OUT_X_L: u16 = 0x28;
const OUT_X_H: u16 = 0x29;
const OUT_Y_L: u16 = 0x2A;
const OUT_Y_H: u16 = 0x2B;
const OUT_Z_L: u16 = 0x2C;
const OUT_Z_H: u16 = 0x2D;
const TEMP_OUT_L: u16 = 0x2E;
const TEMP_OUT_H: u16 = 0x2F;
const INT_CFG: u16 = 0x30;
const INT_SRC: u16 = 0x31;
const INT_THS_L: u16 = 0x32;
const INT_THS_H: u16 = 0x33;
// CTRL_REG1 Configuration
const TEMP_EN: u16 = 0x80; // Enable temperature sensor
const TEMP_DI: u16 = 0x00; // Disable temperature sensor
const OM_LPM: u16 = 0x00; // Low-power mode
const OM_MPM: u16 = 0x20; // Medium-performance mode
const OM_HPM: u16 = 0x40; // High-performance mode
const OM_UHPM: u16 = 0x60; // Ultra-high-performance mode
const DO_0_625: u16 = 0x00; // Output data rate: 0.625Hz
const DO_1_25: u16 = 0x04; // Output data rate: 1.25Hz
const DO_2_5: u16 = 0x08; // Output data rate: 2.5Hz
const DO_5: u16 = 0x0C; // Output data rate: 5Hz
const DO_10: u16 = 0x10; // Output data rate: 10Hz
const DO_20: u16 = 0x14; // Output data rate: 20Hz
const DO_40: u16 = 0x18; // Output data rate: 40Hz
const DO_80: u16 = 0x1C; // Output data rate: 80Hz
const FAST_ODR_DI: u16 = 0x00; // Fast_ODR disabled
const FAST_ODR_EN: u16 = 0x02; // Fast_ODR enabled
const ST_DI: u16 = 0x00; // Self-test disabled
const ST_EN: u16 = 0x01; // Self-test enabled
                         // CTRL_REG2 Configuration
const FS_4: u16 = 0x00; // Full-scale: ±4 gauss
const FS_8: u16 = 0x20; // Full-scale: ±8 gauss
const FS_12: u16 = 0x40; // Full-scale: ±12 gauss
const FS_16: u16 = 0x60; // Full-scale: ±16 gauss
const REBOOT_NM: u16 = 0x00; // Reboot memory content: normal mode
const REBOOT_RMC: u16 = 0x08; // Reboot memory content: reboot memory content
const SOFT_RST: u16 = 0x04; // Reset operation
                            // CTRL_REG3 Configuration
const LP: u16 = 0x20; // Low-power mode configuration
const SPI_4: u16 = 0x00; // SPI serial interface mode selection: 4-wire interface
const SPI_3: u16 = 0x04; // SPI serial interface mode selection: 3-wire interface
const MD_CCM: u16 = 0x00; // Continuous-conversion mode
const MD_SCM: u16 = 0x01; // Single-conversion mode
const MD_PDM: u16 = 0x02; // Power-down mode
const MD_PDM_2: u16 = 0x03; // Power-down mode 2
                            // CTRL_REG4 Configuration
const OMZ_LPM: u16 = 0x00; // Operating mode for Z-axis: low-power mode
const OMZ_MPM: u16 = 0x04; // Operating mode for Z-axis: medium-performance mode
const OMZ_HPM: u16 = 0x08; // Operating mode for Z-axis: high-performance mode
const OMZ_UHPM: u16 = 0x0C; // Operating mode for Z-axis: ultra-high-performance mode
const BLE_LSB: u16 = 0x00; // Big/Little Endian data selection: data LSb at lower address
const BLE_MSB: u16 = 0x02; // Big/Little Endian data selection: data MSb at lower address
                           // CTRL_REG5 Configuration
const FAST_READ_DI: u16 = 0x00; // FAST_READ disabled
const FAST_READ_EN: u16 = 0x80; // FAST_READ enabled
const BDU_CU: u16 = 0x00; // Block data update for magnetic data: continuous update
const BDU_OR: u16 = 0x40; // Block data update for magnetic data: output registers not updated until MSb and LSb have been read)
                          // Sensitivity
const SENSITIVITY_4: u16 = 6842; // Magnetic sensor sensitivity at FS=±4 gauss [LSB/gauss]
const SENSITIVITY_8: u16 = 3421; // Magnetic sensor sensitivity at FS=±8 gauss [LSB/gauss]
const SENSITIVITY_12: u16 = 2281; // Magnetic sensor sensitivity at FS=±12 gauss [LSB/gauss]
const SENSITIVITY_16: u16 = 1711; // Magnetic sensor sensitivity at FS=±16 gauss [LSB/gauss]
const SENSITIVITY_TEMP: u16 = 8; // Temperature sensitivity [LSB/°C] (@ Vdd = 2.5 V, T = 25 °C)

pub struct LIS3MDLTR {
    bus: u8,
    address: u16,
}

impl LIS3MDLTR {
    pub fn new(bus: u8, address: u16) -> Self {
        Self { bus, address }
    }
    pub fn configure(&self) -> Result<(), LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;

        self.configure_2(&mut dev, true)?;
        self.configure_1(&mut dev)?;
        self.configure_2(&mut dev, false)?;
        self.configure_3(&mut dev)?;
        self.configure_4(&mut dev)?;
        self.configure_5(&mut dev)?;

        Ok(())
    }
    fn configure_1(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        let config = TEMP_EN | OM_MPM | DO_10 | FAST_ODR_DI | ST_DI;
        dev.smbus_write_byte_data(CTRL_REG1 as u8, config as u8)?;

        Ok(())
    }
    fn configure_2(&self, dev: &mut LinuxI2CDevice, reset: bool) -> Result<(), LinuxI2CError> {
        let mut config: u16;
        if reset {
            config = SOFT_RST;
        } else {
            config = FS_4 | REBOOT_NM;
        }
        dev.smbus_write_byte_data(CTRL_REG2 as u8, config as u8)?;

        Ok(())
    }
    fn configure_3(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        let config = MD_CCM;
        dev.smbus_write_byte_data(CTRL_REG3 as u8, config as u8)?;

        Ok(())
    }
    fn configure_4(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        let config = OMZ_MPM | BLE_LSB;
        dev.smbus_write_byte_data(CTRL_REG4 as u8, config as u8)?;

        Ok(())
    }
    fn configure_5(&self, dev: &mut LinuxI2CDevice) -> Result<(), LinuxI2CError> {
        let config = FAST_READ_DI | BDU_CU;
        dev.smbus_write_byte_data(CTRL_REG5 as u8, config as u8)?;

        Ok(())
    }
    fn read_mag_x(&self) -> Result<f32, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let out_x_h = dev.smbus_read_byte_data(OUT_X_H as u8)?;
        let out_x_l = dev.smbus_read_byte_data(OUT_X_L as u8)?;
        let out_x_adc = (((out_x_h as u16) << 8) | out_x_l as u16) & 0xFFFF;
        let mag_x = self.adc_to_gauss(out_x_adc, SENSITIVITY_4);

        Ok(mag_x)
    }
    fn read_mag_y(&self) -> Result<f32, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let out_y_h = dev.smbus_read_byte_data(OUT_Y_H as u8)?;
        let out_y_l = dev.smbus_read_byte_data(OUT_Y_L as u8)?;
        let out_y_adc = (((out_y_h as u16) << 8) | out_y_l as u16) & 0xFFFF;
        let mag_y = self.adc_to_gauss(out_y_adc, SENSITIVITY_4);

        Ok(mag_y)
    }
    fn read_mag_z(&self) -> Result<f32, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let out_z_h = dev.smbus_read_byte_data(OUT_Z_H as u8)?;
        let out_z_l = dev.smbus_read_byte_data(OUT_Z_L as u8)?;
        let out_z_adc = (((out_z_h as u16) << 8) | out_z_l as u16) & 0xFFFF;
        let mag_z = self.adc_to_gauss(out_z_adc, SENSITIVITY_4);

        Ok(mag_z)
    }
    pub fn read_mag(&self) -> Result<[f32; 3], LinuxI2CError> {
        let mag_x = self.read_mag_x()?;
        let mag_y = self.read_mag_y()?;
        let mag_z = self.read_mag_z()?;
        // let mag_t = (mag_x.powf(2.0) + mag_y.powf(2.0) + mag_z.powf(2.0)).sqrt();
        let mag = [mag_x, mag_y, mag_z];

        Ok(mag)
    }
    fn adc_to_gauss(&self, mut adc: u16, sensitifity: u16) -> f32 {
        let mut sign: f32 = 1.0;
        if adc >= 0x8000 {
            sign = -1.0;
            adc = 0xFFFF - adc;
        }

        adc as f32 * sign / sensitifity as f32
    }
    pub fn read_id(&self) -> Result<u8, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let id = dev.smbus_read_byte_data(WHO_AM_I as u8)?;

        Ok(id)
    }
    pub fn read_temp(&self) -> Result<f32, LinuxI2CError> {
        let mut dev = LinuxI2CDevice::new(&format!("/dev/i2c-{}", self.bus), self.address)?;
        let temp_h = dev.smbus_read_byte_data(TEMP_OUT_H as u8)?;
        let temp_l = dev.smbus_read_byte_data(TEMP_OUT_L as u8)?;
        let mut temp_adc = (((temp_h as u16) << 8) | (temp_l as u16)) & 0xFFFF;

        let mut sign: f32 = 1.0;
        if temp_adc >= 0x8000 {
            sign = -1.0;
            temp_adc = 0xFFFF - temp_adc;
        }

        let temp = (temp_adc as f32) * sign / SENSITIVITY_TEMP as f32 + 25.0;

        Ok(temp)
    }
}
