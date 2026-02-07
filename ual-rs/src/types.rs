#![no_std]

/// 16-bit Semantic ID
pub type SemanticID = u16;

#[derive(Debug)]
pub enum UALError {
    BufferTooSmall,
    InvalidID,
}

pub type UALResult<T> = Result<T, UALError>;

/// A simplified message structure for embedded devices
pub struct UALMessage {
    pub action_id: SemanticID,
    // On embedded, we might use fixed size arrays or references
    pub target_id: SemanticID,
    pub value: i32,
}
