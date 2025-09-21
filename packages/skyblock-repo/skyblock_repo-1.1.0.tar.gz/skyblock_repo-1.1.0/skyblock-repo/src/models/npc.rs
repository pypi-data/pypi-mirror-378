#[cfg(feature = "python")]
use pyo3::{pyclass, pymethods};
use serde::{Deserialize, Serialize};
#[cfg(feature = "python")]
use skyblock_repo_macros::PyStr;

use crate::models::Coordinates;

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct SkyblockNpc {
	#[serde(default)]
	pub internal_id: String,
	pub name: Option<String>,
	pub flags: Option<NpcFlags>,
	pub location: Option<NpcLocation>,
	pub visitor: Option<NpcGardenVisitor>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct NpcFlags {
	pub merchant: bool,
	pub abiphone: bool,
	pub garden: bool,
	pub shop: bool,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct NpcLocation {
	pub zone: Option<String>,
	pub coordinates: Option<Coordinates>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct NpcGardenVisitor {
	pub rarity: String,
	pub garden_level: u8,
	pub desire: Option<String>,
	pub bonus: Option<String>,
	pub copper: Option<f64>,
	pub farming_xp: Option<f64>,
}
