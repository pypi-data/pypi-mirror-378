use crate::helper::rb_type::RBError;
use crate::rb_control::rb_gpioe;

pub fn disable_rf_input() -> Result<(), RBError> {
    rb_gpioe::disable_nb3v9312c_gpioe()?;
    rb_gpioe::rf_input_select_gpioe(0)?;

    Ok(())
}

pub fn enable_sma_input() -> Result<(), RBError> {
    rb_gpioe::disable_nb3v9312c_gpioe()?;
    rb_gpioe::rf_input_select_gpioe(2)?;

    Ok(())
}

pub fn enable_tca_input() -> Result<(), RBError> {
    rb_gpioe::enable_nb3v9312c_gpioe()?;
    rb_gpioe::rf_input_select_gpioe(1)?;

    Ok(())
}
