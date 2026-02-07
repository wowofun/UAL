#![no_std]

//! # UAL Embedded (ual-rs)
//! 
//! A `no_std` implementation of the Universal Agent Language protocol designed for 
//! microcontrollers (STM32, ESP32, nRF52).
//! 
//! ## Architecture
//! - **Zero Allocation**: Uses `heapless` structures to avoid dynamic memory allocation.
//! - **Static Atlas**: Compile-time generated semantic map for extreme performance.
//! - **Streaming Codec**: Processes byte streams byte-by-byte for minimal buffer usage.

pub mod atlas;
pub mod codec;
pub mod types;

use codec::Encoder;
use types::{UALMessage, UALResult};

/// Main UAL Agent struct for Embedded Systems
pub struct MicroAgent<'a> {
    id: &'a str,
    encoder: Encoder,
}

impl<'a> MicroAgent<'a> {
    pub fn new(id: &'a str) -> Self {
        Self {
            id,
            encoder: Encoder::new(),
        }
    }

    /// Encodes a semantic message into a fixed-size buffer
    pub fn encode_into(&self, msg: &UALMessage, buffer: &mut [u8]) -> UALResult<usize> {
        self.encoder.encode(msg, buffer)
    }
}
