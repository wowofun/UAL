#![no_std]

use crate::types::{SemanticID, UALError, UALResult, UALMessage};

pub struct Encoder;

impl Encoder {
    pub fn new() -> Self {
        Self
    }

    /// Encodes a UALMessage into a byte slice.
    /// Returns the number of bytes written.
    pub fn encode(&self, msg: &UALMessage, buffer: &mut [u8]) -> UALResult<usize> {
        // Simple mock encoding logic: 
        // [Header: 0xUA] [ActionID: u16] [PayloadLen: u8] [Payload...]
        
        if buffer.len() < 4 {
            return Err(UALError::BufferTooSmall);
        }

        buffer[0] = 0x55; // 'U'
        buffer[1] = 0x41; // 'A'
        
        // Mock packing action ID
        let action_id = msg.action_id;
        buffer[2] = (action_id >> 8) as u8;
        buffer[3] = (action_id & 0xFF) as u8;
        
        Ok(4) // Mock length
    }
}
