use crate::constant::*;

use crate::device::{pca9548a, si5345b};
use crate::helper::rb_type::RBError;

pub fn configure_clk_synth() -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_SI5345B_CHANNEL)?;

    let si5345b = si5345b::SI5345B::new(I2C_BUS, RB_SI5345B_ADDRESS);
    si5345b.configure_si5345b()?;
    
    i2c_mux.reset()?;

    Ok(())
}

pub fn program_nvm_clk_synth(verbose: bool) -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_SI5345B_CHANNEL)?;

    let si5345b = si5345b::SI5345B::new(I2C_BUS, RB_SI5345B_ADDRESS);

    // Check how many user banks available
    let available_nvm_bank = si5345b.read_available_nvm_bank()?;
    match available_nvm_bank {
        2 => {
            if verbose {
                println!("Number of User Banks Available to Burn: 2");
            }
        },
        1 => {
            if verbose {
                println!("Number of User Banks Available to Burn: 1");
            }
        }
        0 => {
            println!("Number of User Banks Available to Burn: 0");
            println!("Exiting the program...");
            std::process::exit(1);
        }
        _ => {
            println!("ACTIVE_NVM_BANK Error");
            println!("Exiting the program...");
            std::process::exit(1);
        }
    }

    // Program SI5345B NVM
    if verbose {
        println!("Programming SI5345B NVM...");
    }
    si5345b.configure_nvm_si5345b()?;
    if verbose {
        println!("Done programming SI5345B NVM");
    }
    
    i2c_mux.reset()?;

    if verbose {
        println!("Complete programming SI5345B NVM!");
    }

    Ok(())
}


pub fn reset_clk_synth(rst_type: u8) -> Result<(), RBError> {
    let i2c_mux = pca9548a::PCA9548A::new(I2C_BUS, RB_PCA9548A_ADDRESS_2);
    i2c_mux.select(RB_SI5345B_CHANNEL)?;

    let si5345b = si5345b::SI5345B::new(I2C_BUS, RB_SI5345B_ADDRESS);

    match rst_type {
        0 => {
            si5345b.soft_reset_si5345b()?;
            si5345b.configure_si5345b()?;
        }
        1 => {
            si5345b.hard_reset_si5345b()?;
        }
        _ => {},
    }

    i2c_mux.reset()?;

    Ok(())
}
