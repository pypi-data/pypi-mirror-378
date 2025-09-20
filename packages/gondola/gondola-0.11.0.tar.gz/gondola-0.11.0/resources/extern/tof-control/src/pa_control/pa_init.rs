use crate::helper::pa_type::{PASetBias, PAError};

pub fn initialize() -> Result<(), PAError> {
    // initialize_bias()?;
    initialize_bias_manual()?;

    Ok(())
}

// fn initialize_bias() -> Result<(), PAError> {
//     PASetBias::set_bias()?;

//     Ok(())
// }

fn initialize_bias_manual() -> Result<(), PAError> {
    PASetBias::set_manual_bias(None, 58.0)?;

    Ok(())
}