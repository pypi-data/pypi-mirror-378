use log::{trace, warn};
use std::error::Error;
use std::fs::File;

use memmap::{Mmap, MmapMut};

use crate::constant::*;

pub const SIZEOF_U32: usize = 4;

#[derive(Debug, Copy, Clone)]
pub struct RegisterError {}

pub fn map_physical_mem_read(
    addr_space: &str,
    addr: u32,
    len: usize,
) -> Result<Mmap, Box<dyn Error>> {
    let m = unsafe {
        memmap::MmapOptions::new()
            .offset(addr as u64)
            .len(len)
            .map(&File::open(addr_space)?)?
    };
    Ok(m)
}

pub fn map_physical_mem_write(
    addr_space: &str,
    addr: u32,
    len: usize,
) -> Result<MmapMut, Box<dyn Error>> {
    let m = unsafe {
        memmap::MmapOptions::new()
            .offset(addr as u64)
            .len(len)
            .map_mut(&File::options().read(true).write(true).open(addr_space)?)?
    };
    Ok(m)
}

pub fn read_control_reg(addr: u32) -> Result<u32, RegisterError>
where
    u32: std::fmt::LowerHex,
{
    let m = match map_physical_mem_read(RB_UIO0, addr, SIZEOF_U32) {
        Ok(m) => m,
        Err(err) => {
            let error = RegisterError {};
            warn!("Failed to mmap: Err={:?}", err);
            return Err(error);
        }
    };
    let p = m.as_ptr() as *const u32;
    let value: u32;
    unsafe {
        value = std::ptr::read_volatile(p.offset(0));
    }
    Ok(value)
}

pub fn write_control_reg(addr: u32, data: u32) -> Result<(), RegisterError>
where
    u32: std::fmt::LowerHex,
{
    trace!("Attempting to write {data} at addr {addr}");

    let m = match map_physical_mem_write(RB_UIO0, addr, SIZEOF_U32) {
        Ok(m) => m,
        Err(err) => {
            let error = RegisterError {};
            warn!("[write_control_reg] Failed to mmap: Err={:?}", err);
            return Err(error);
        }
    };
    let p = m.as_ptr() as *mut u32;
    unsafe {
        std::ptr::write_volatile(p.offset(0), data);
    }
    Ok(())
}
