// core/src/models/graph/message.rs
//! ERN Message types

use super::{Deal, MessageHeader, Party, Release, Resource};
use crate::models::{versions::ERNVersion, AttributeMap, Comment, Extensions};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ERNMessage {
    pub message_header: MessageHeader,
    pub parties: Vec<Party>,
    pub resources: Vec<Resource>,
    pub releases: Vec<Release>,
    pub deals: Vec<Deal>,
    pub version: ERNVersion,
    pub profile: Option<ERNProfile>,
    pub message_audit_trail: Option<MessageAuditTrail>,
    /// All XML attributes (standard and custom) for the root element
    pub attributes: Option<AttributeMap>,
    /// Comprehensive extension preservation system
    pub extensions: Option<Extensions>,
    /// Legacy extensions (for backward compatibility)
    pub legacy_extensions: Option<std::collections::HashMap<String, String>>,
    pub comments: Option<Vec<Comment>>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum ERNProfile {
    AudioAlbum,
    AudioSingle,
    Video,
    Mixed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MessageAuditTrail {
    pub audit_trail_events: Vec<AuditTrailEvent>,
    /// All XML attributes (standard and custom)
    pub attributes: Option<AttributeMap>,
    /// Extensions for audit trail
    pub extensions: Option<Extensions>,
    /// Comments associated with audit trail
    pub comments: Option<Vec<Comment>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditTrailEvent {
    pub message_audit_trail_event_reference: String,
    pub message_audit_trail_event_type: String,
    pub date_time: chrono::DateTime<chrono::Utc>,
    pub responsible_party_reference: Option<String>,
    /// All XML attributes (standard and custom)
    pub attributes: Option<AttributeMap>,
    /// Extensions for individual audit trail events
    pub extensions: Option<Extensions>,
    /// Comments associated with this audit trail event
    pub comments: Option<Vec<Comment>>,
}

impl ERNMessage {
    pub fn to_build_request(&self) -> Self {
        self.clone()
    }
}
