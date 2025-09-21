use crate::constant::*;
use crate::helper::rb_type::RBError;
use crate::device::{ad5675, pca9548a};

pub fn set_dac() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_AD5675_CHANNEL)?;
    let ad5675 = ad5675::AD5675::new(RB_AD5675_ADDRESS);

    /*	DAC settings
        Next few lines will configure the DAC outputs for DRS4/analog front end
        The AD5675 is a 16-bit DAC with range 0 to 2.048 V
        Decimal step size is: 0.00003125 V / integer

        DAC Channels:
            0x0: Vout -
            0x1: Vout +
            0X2: ROFS
            0X3: THS4509 Common Voltage
            0X4: DRS BIAS
    */

    // DRS4 analog input offset/bias: IN+_OFS, IN-_OFS
    // in_neg
    ad5675.write_dac(0, 25600);
    // in_pos
    ad5675.write_dac(1, 25600);
    // offset
    // DRS ROFS 1V, 1.6V max
    // ad5675.write_dac(2, 35200);
    ad5675.write_dac(2, 42500);
    // THS4509 common mode voltage: V_CM
    // For +3.5 V and -1.5 V split supply, half range is 1 V
    ad5675.write_dac(3, 32000);
    // DRS BIAS 0.7V
    ad5675.write_dac(4, 22400);

    i2c_mux.reset()?;

    Ok(())
    
}

pub fn set_dac_500() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_AD5675_CHANNEL)?;
    let ad5675 = ad5675::AD5675::new(RB_AD5675_ADDRESS);

    ad5675.write_dac(2, 49600);

    i2c_mux.reset()?;

    Ok(())
}

pub fn dac_noi_mode() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_AD5675_CHANNEL)?;
    let ad5675 = ad5675::AD5675::new(RB_AD5675_ADDRESS);

    ad5675.write_dac(1, 25600);

    i2c_mux.reset()?;

    Ok(())
}

pub fn dac_vcal_mode() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_AD5675_CHANNEL)?;
    let ad5675 = ad5675::AD5675::new(RB_AD5675_ADDRESS);

    ad5675.write_dac(1, 46400);

    i2c_mux.reset()?;

    Ok(())
}

pub fn dac_tcal_mode() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_AD5675_CHANNEL)?;
    let ad5675 = ad5675::AD5675::new(RB_AD5675_ADDRESS);

    ad5675.write_dac(1, 25600);

    i2c_mux.reset()?;

    Ok(())
}

pub fn dac_sma_mode() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_AD5675_CHANNEL)?;
    let ad5675 = ad5675::AD5675::new(RB_AD5675_ADDRESS);

    ad5675.write_dac(1, 25600);

    i2c_mux.reset()?;

    Ok(())
}
