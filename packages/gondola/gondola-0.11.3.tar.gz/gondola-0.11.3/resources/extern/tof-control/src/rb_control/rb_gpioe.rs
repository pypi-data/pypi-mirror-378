use std::thread;
use std::time::Duration;

use crate::constant::*;
use crate::helper::rb_type::RBError;
use crate::device::cy8c9560a::CY8C9560A;
use crate::device::{cy8c9560a, pca9548a};

/*
Ports used for Readout Board V2.5.2
cy8c9560A
//////////////////////////////////////////
//Output
//////////////////////////////////////////

GP0[7]
GP0[7]: Si5345_FINC

GP1[]

GP2[1:0]
GP2[1]: HMC849_EN3
GP2[0]: HMC849_VCTL3

GP3[5:4,2:0]
GP3[5]: MARS_WDI_GE
GP3[4]: ~VCAL_RST
GP3[2]: Si5345_FDEC
GP3[1]: ~Si5345_OE
GP3[0]: ~Si5345_RST

GP4[7:2]
GP4[7]: HMC849_VCTL6
GP4[6]: HMC849_EN6
GP4[5]: HMC849_VCTL7
GP4[4]: HMC849_EN7
GP4[3]: HMC849_VCTL8
GP4[2]: HMC849_EN8

GP5[5:4,1:0]
GP5[5]: HMC849_EN5
GP5[4]: HMC849_VCTL5
GP5[1]: HMC849_VCTL4
GP5[0]: HMC849_EN4

GP6[]

GP7[7:0]
GP7[7]: TCA_CLK_SC_EN
GP7[6]: TCA_CLK_OUT_EN
GP7[5]: HMC849_EN0
GP7[4]: HMC849_VCTL0
GP7[3]: HMC849_EN1
GP7[2]: HMC849_VCTL1
GP7[1]: HMC849_EN2
GP7[0]: HMC849_VCTL2

Initialization Value:
GP0: 0x00
GP1: 0xFF
GP2: 0x03
GP3: 0x13
GP4: 0xFC
GP5: 0x33
GP6: 0xFF
GP7: 0x3F

*/

pub fn initialize_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);

    // Port 0
    cy8c9560a.select_port(0)?;
    cy8c9560a.set_interrupt_mask_port(0x00)?;
    cy8c9560a.set_pin_direction(0x00)?;
    cy8c9560a.set_drive_mode(4)?;

    // Port 1
    cy8c9560a.select_port(1)?;
    cy8c9560a.set_interrupt_mask_port(0x00)?;
    cy8c9560a.set_pin_direction(0x00)?;
    cy8c9560a.set_drive_mode(1)?;

    // Port 2
    cy8c9560a.select_port(2)?;
    cy8c9560a.set_interrupt_mask_port(0x00)?;
    cy8c9560a.set_pin_direction(0x00)?;
    cy8c9560a.set_drive_mode(4)?;

    // Port 3
    cy8c9560a.select_port(3)?;
    cy8c9560a.set_interrupt_mask_port(0x00)?;
    cy8c9560a.set_pin_direction(0x00)?;
    cy8c9560a.set_drive_mode(4)?;

    // Port 4
    cy8c9560a.select_port(4)?;
    cy8c9560a.set_interrupt_mask_port(0x00)?;
    cy8c9560a.set_pin_direction(0x00)?;
    cy8c9560a.set_drive_mode(4)?;

    // Port 5
    cy8c9560a.select_port(5)?;
    cy8c9560a.set_interrupt_mask_port(0x00)?;
    cy8c9560a.set_pin_direction(0x00)?;
    cy8c9560a.set_drive_mode(4)?;

    // Port 6
    cy8c9560a.select_port(6)?;
    cy8c9560a.set_interrupt_mask_port(0x00)?;
    cy8c9560a.set_pin_direction(0x00)?;
    cy8c9560a.set_drive_mode(1)?;

    // Port 7
    cy8c9560a.select_port(7)?;
    cy8c9560a.set_interrupt_mask_port(0x00)?;
    cy8c9560a.set_pin_direction(0x00)?;
    cy8c9560a.set_drive_mode(4)?;

    // Set ouput ports
    cy8c9560a.set_output_port(0, 0x00)?;
    cy8c9560a.set_output_port(1, 0xFF)?;
    cy8c9560a.set_output_port(2, 0x03)?;
    cy8c9560a.set_output_port(3, 0x13)?;
    cy8c9560a.set_output_port(4, 0xFC)?;
    cy8c9560a.set_output_port(5, 0x33)?;
    cy8c9560a.set_output_port(6, 0xFF)?;
    cy8c9560a.set_output_port(7, 0x3F)?;

    i2c_mux.reset()?;

    Ok(())
}

pub fn reset_si5345b_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let mut value = cy8c9560a.read_port_status(3)?;
    value = value ^ 0x01;
    cy8c9560a.set_output_port(3, value)?;
    value = cy8c9560a.read_port_status(3)?;
    value = value | 0x01;
    cy8c9560a.set_output_port(3, value)?;

    i2c_mux.reset()?;

    thread::sleep(Duration::from_millis(2000));

    Ok(())
}

pub fn enable_si5345b_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let mut value = cy8c9560a.read_port_status(3)?;
    value = (value & !0x02) | 0 << 1;
    cy8c9560a.set_output_port(3, value)?;

    i2c_mux.reset()?;

    Ok(())
}

pub fn enable_ad5675_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let mut value = cy8c9560a.read_port_status(3)?;
    value = (value & !0x10) | 1 << 4;
    cy8c9560a.set_output_port(3, value)?;

    i2c_mux.reset()?;

    Ok(())
}

// GP7[7]: TCA_CLK_SC_EN
// GP7[6]: TCA_CLK_OUT_EN
pub fn enable_nb3v9312c_gpioe() -> Result<(), RBError>  {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let mut value = cy8c9560a.read_port_status(7)?;
    value = value | 0xC0;
    cy8c9560a.set_output_port(7, value)?;

    i2c_mux.reset()?;

    Ok(())
}
pub fn disable_nb3v9312c_gpioe() -> Result<(), RBError>  {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let mut value = cy8c9560a.read_port_status(7)?;
    value = value & 0x3F;
    cy8c9560a.set_output_port(7, value)?;

    i2c_mux.reset()?;

    Ok(())
}

/*
  HMC849 Truth Table:
 |_VCTL__|__EN__|  |_RFC -> RF1_|_RFC -> RF2_|
    0    |   0           OFF    |     ON
    1    |   0           ON           OFF
    0    |   1           OFF          OFF
    1    |   1           OFF          OFF

    hmcChannel: 0 - 8
    mode: 0: RFC = OFF  (No Connection)
          1: RFC -> RF1 (TCA Calibration Input)
          2: RFC -> RF2 (SMA Input)

*/
pub fn rf_input_select_gpioe(mode: u8) -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    drs_ch1_input_select(cy8c9560a, mode)?;
    drs_ch2_input_select(cy8c9560a, mode)?;
    drs_ch3_input_select(cy8c9560a, mode)?;
    drs_ch4_input_select(cy8c9560a, mode)?;
    drs_ch5_input_select(cy8c9560a, mode)?;
    drs_ch6_input_select(cy8c9560a, mode)?;
    drs_ch7_input_select(cy8c9560a, mode)?;
    drs_ch8_input_select(cy8c9560a, mode)?;
    drs_ch9_input_select(cy8c9560a, mode)?;

    Ok(())
}

// GP7[5] = EN
// GP7[4] = VCTL
fn drs_ch1_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(7)?;

    match mode {
        0 => {
            let value = port_status | 0x30;
            gpioe.set_output_port(7, value)?;
        }
        1 => {
            let value = (port_status & !0x30) | 0x10;
            gpioe.set_output_port(7, value)?;
        }
        2 => {
            let value = (port_status & !0x30) | 0x00;
            gpioe.set_output_port(7, value)?;
        }
        _ => {
            gpioe.set_output_port(7, port_status)?;
        }
    }

    Ok(())
}

// GP7[3] = EN
// GP7[2] = VCTL
fn drs_ch2_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(7)?;

    match mode {
        0 => {
            let value = port_status | 0x0C;
            gpioe.set_output_port(7, value)?;
        }
        1 => {
            let value = (port_status & !0x0C) | 0x04;
            gpioe.set_output_port(7, value)?;
        }
        2 => {
            let value = (port_status & !0x0C) | 0x00;
            gpioe.set_output_port(7, value)?;
        }
        _ => {
            gpioe.set_output_port(7, port_status)?;
        }
    }

    Ok(())
}

// GP7[1] = EN
// GP7[0] = VCTL
fn drs_ch3_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(7)?;

    match mode {
        0 => {
            let value = port_status | 0x03;
            gpioe.set_output_port(7, value)?;
        }
        1 => {
            let value = (port_status & !0x03) | 0x01;
            gpioe.set_output_port(7, value)?;
        }
        2 => {
            let value = (port_status & !0x03) | 0x00;
            gpioe.set_output_port(7, value)?;
        }
        _ => {
            gpioe.set_output_port(7, port_status)?;
        }
    }

    Ok(())
}

// GP2[1] = EN
// GP2[0] = VCTL
fn drs_ch4_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(2)?;

    match mode {
        0 => {
            let value = port_status | 0x03;
            gpioe.set_output_port(2, value)?;
        }
        1 => {
            let value = (port_status & !0x03) | 0x01;
            gpioe.set_output_port(2, value)?;
        }
        2 => {
            let value = (port_status & !0x03) | 0x00;
            gpioe.set_output_port(2, value)?;
        }
        _ => {
            gpioe.set_output_port(2, port_status)?;
        }
    }

    Ok(())
}

// GP5[1] = VCTL
// GP5[0] = EN
fn drs_ch5_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(5)?;

    match mode {
        0 => {
            let value = port_status | 0x03;
            gpioe.set_output_port(5, value)?;
        }
        1 => {
            let value = (port_status & !0x03) | 0x02;
            gpioe.set_output_port(5, value)?;
        }
        2 => {
            let value = (port_status & !0x03) | 0x00;
            gpioe.set_output_port(5, value)?;
        }
        _ => {
            gpioe.set_output_port(5, port_status)?;
        }
    }

    Ok(())
}

// GP5[5] = EN
// GP5[4] = VCTL
fn drs_ch6_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(5)?;

    match mode {
        0 => {
            let value = port_status | 0x30;
            gpioe.set_output_port(5, value)?;
        }
        1 => {
            let value = (port_status & !0x30) | 0x10;
            gpioe.set_output_port(5, value)?;
        }
        2 => {
            let value = (port_status & !0x30) | 0x00;
            gpioe.set_output_port(5, value)?;
        }
        _ => {
            gpioe.set_output_port(5, port_status)?;
        }
    }

    Ok(())
}

// GP4[7] = VCTL
// GP4[6] = EN
fn drs_ch7_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(4)?;

    match mode {
        0 => {
            let value = port_status | 0xC0;
            gpioe.set_output_port(4, value)?;
        }
        1 => {
            let value = (port_status & !0xC0) | 0x80;
            gpioe.set_output_port(4, value)?;
        }
        2 => {
            let value = (port_status & !0xC0) | 0x00;
            gpioe.set_output_port(4, value)?;
        }
        _ => {
            gpioe.set_output_port(4, port_status)?;
        }
    }

    Ok(())
}

// GP4[5] = VCTL
// GP4[4] = EN
fn drs_ch8_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(4)?;

    match mode {
        0 => {
            let value = port_status | 0x30;
            gpioe.set_output_port(4, value)?;
        }
        1 => {
            let value = (port_status & !0x30) | 0x20;
            gpioe.set_output_port(4, value)?;
        }
        2 => {
            let value = (port_status & !0x30) | 0x00;
            gpioe.set_output_port(4, value)?;
        }
        _ => {
            gpioe.set_output_port(4, port_status)?;
        }
    }

    Ok(())
}

// GP4[3] = VCTL
// GP4[2] = EN
fn drs_ch9_input_select(gpioe: CY8C9560A, mode: u8) -> Result<(), RBError> {
    let port_status = gpioe.read_port_status(4)?;

    match mode {
        0 => {
            let value = port_status | 0x0C;
            gpioe.set_output_port(4, value)?;
        }
        1 => {
            let value = (port_status & !0x0C) | 0x08;
            gpioe.set_output_port(4, value)?;
        }
        2 => {
            let value = (port_status & !0x0C) | 0x00;
            gpioe.set_output_port(4, value)?;
        }
        _ => {
            gpioe.set_output_port(4, port_status)?;
        }
    }

    Ok(())
}


pub fn device_info_gpioe() -> Result<(u8, u8, Vec<u8>), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let (device_family, device_setting) = cy8c9560a.read_device_info()?;
    let mut port_status = Vec::new();
    for i in 0..=7 {
        port_status.push(cy8c9560a.read_port_status(i)?);
    }

    Ok((
        device_family,
        device_setting,
        port_status,
    ))
}

pub fn read_port_gpioe() -> Result<Vec<u8>, RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let mut gp = Vec::new();
    for i in 0..=7 {
        gp.push(cy8c9560a.read_port_status(i)?);
    }

    i2c_mux.reset()?;

    Ok(gp)
}

pub fn set_rf_switch_gpioe(mode: u8) -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);

    for i in 0..=8 {
        if i == 8 {
            match mode {
                0 => cy8c9560a.set_rf_switch(i, 0)?,
                _ => cy8c9560a.set_rf_switch(i, 2)?,
            }
        } else {
            cy8c9560a.set_rf_switch(i, mode)?
        }
    }

    i2c_mux.reset()?;

    Ok(())
}

pub fn enable_tcal_clock_gpioe(mode: u8) -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    if mode == 1 {
        cy8c9560a.enable_tcal_clock()?;
    }

    i2c_mux.reset()?;

    Ok(())
}

pub fn disable_tcal_clock_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    cy8c9560a.disable_tcal_clock()?;

    i2c_mux.reset()?;

    Ok(())
}

pub fn dac_reset_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let mut value = cy8c9560a.read_port_status(3)?;
    value = (value & !0x10) | 0x10;
    cy8c9560a.set_output_port(3, value)?;

    i2c_mux.reset()?;

    Ok(())
}

pub fn program_eeprom_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let enable_register = cy8c9560a.read_enable_register()?;
    if (enable_register & 0x02) != 0x02 {
        cy8c9560a.enable_eeprom()?;
    }

    cy8c9560a.store_config_eeprom_por()?;

    i2c_mux.reset()?;
    
    Ok(())
}

pub fn reset_eeprom_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let enable_register = cy8c9560a.read_enable_register()?;
    if (enable_register & 0x02) != 0x02 {
        cy8c9560a.enable_eeprom()?;
    }

    cy8c9560a.reset_config_eeprom_por()?;

    i2c_mux.reset()?;
    
    Ok(())
}

pub fn reset_gpioe() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    cy8c9560a.initialize_all_outputs()?;

    i2c_mux.reset()?;
    
    Ok(())
}

pub fn read_rf_input_port(ch: u8) -> Result<u8, RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_CY8C9560A_CHANNEL)?;

    let cy8c9560a = cy8c9560a::CY8C9560A::new(I2C_BUS, RB_CY8C9560A_ADDRESS);
    let mut rf_input_port: u8 = Default::default();
    match ch {

        1 => {
            rf_input_port = cy8c9560a.read_port_status(7)?;
            rf_input_port = (rf_input_port & 0x30) >> 4;
        }
        2 => {
            rf_input_port = cy8c9560a.read_port_status(7)?;
            rf_input_port = (rf_input_port & 0x0C) >> 2;
        }
        3 => {
            rf_input_port = cy8c9560a.read_port_status(7)?;
            rf_input_port = rf_input_port & 0x03;
        }
        4 => {
            rf_input_port = cy8c9560a.read_port_status(2)?;
            rf_input_port = rf_input_port & 0x03;
        }
        5 => {
            rf_input_port = cy8c9560a.read_port_status(5)?;
            rf_input_port = rf_input_port & 0x03;
            rf_input_port = ((rf_input_port & 0x02) >> 1) | ((rf_input_port & 0x01) << 1)
        }
        6 => {
            rf_input_port = cy8c9560a.read_port_status(5)?;
            rf_input_port = (rf_input_port & 0x30) >> 4;
        }
        7 => {
            rf_input_port = cy8c9560a.read_port_status(4)?;
            rf_input_port = (rf_input_port & 0xC0) >> 6;
            rf_input_port = ((rf_input_port & 0x02) >> 1) | ((rf_input_port & 0x01) << 1)
        }
        8 => {
            rf_input_port = cy8c9560a.read_port_status(4)?;
            rf_input_port = (rf_input_port & 0x30) >> 4;
            rf_input_port = ((rf_input_port & 0x02) >> 1) | ((rf_input_port & 0x01) << 1)
        }
        9 => {
            rf_input_port = cy8c9560a.read_port_status(4)?;
            rf_input_port = (rf_input_port & 0x0C) >> 2;
            rf_input_port = ((rf_input_port & 0x02) >> 1) | ((rf_input_port & 0x01) << 1)
        }
        _ => {}
    }

    i2c_mux.reset()?;

    Ok(rf_input_port)
}