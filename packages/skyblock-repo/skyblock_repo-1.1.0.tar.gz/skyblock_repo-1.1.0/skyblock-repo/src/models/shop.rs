use std::collections::BTreeMap;

#[cfg(feature = "python")]
use pyo3::{pyclass, pymethods};
use serde::{Deserialize, Serialize};
#[cfg(feature = "python")]
use skyblock_repo_macros::PyStr;

use crate::UpgradeCost;

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct SkyblockShop {
	#[serde(default)]
	pub internal_id: String,
	pub name: Option<String>,
	pub source: Option<String>,
	#[serde(default)]
	pub slots: BTreeMap<String, InventorySlot>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct InventorySlot {
	pub material: Option<String>,
	pub name: Option<String>,
	pub lore: Option<String>,
	#[serde(default)]
	pub cost: Vec<UpgradeCost>,
	#[serde(default)]
	pub output: Vec<UpgradeCost>,
}
