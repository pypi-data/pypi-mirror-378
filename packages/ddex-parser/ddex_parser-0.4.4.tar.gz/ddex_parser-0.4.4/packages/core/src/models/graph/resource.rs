// core/src/models/graph/resource.rs
//! Resource types

use crate::models::{
    common::{Copyright, Identifier, LocalizedString},
    Extensions,
};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Resource {
    pub resource_reference: String,
    pub resource_type: ResourceType,
    pub resource_id: Vec<Identifier>,
    pub reference_title: Vec<LocalizedString>,
    pub duration: Option<std::time::Duration>,
    pub technical_details: Vec<TechnicalDetails>,
    pub rights_controller: Vec<String>,
    pub p_line: Vec<Copyright>,
    pub c_line: Vec<Copyright>,
    /// Extensions for resource
    pub extensions: Option<Extensions>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ResourceType {
    SoundRecording,
    Video,
    Image,
    Text,
    SheetMusic,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TechnicalDetails {
    pub technical_resource_details_reference: String,
    pub audio_codec: Option<String>,
    pub bitrate: Option<i32>,
    pub sample_rate: Option<i32>,
    pub file_format: Option<String>,
    pub file_size: Option<u64>,
    /// Extensions for technical details
    pub extensions: Option<Extensions>,
}
