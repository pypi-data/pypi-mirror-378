#[cfg(feature = "python")]
use pyo3::{pyclass, pymethods};
use serde::{Deserialize, Serialize};
#[cfg(feature = "python")]
use skyblock_repo_macros::PyStr;

pub mod enchantment;
pub mod item;
pub mod npc;
pub mod pet;
pub mod recipe;
pub mod shop;
pub mod zone;

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct UpgradeCost {
	pub r#type: Option<UpgradeType>,
	pub item_id: Option<String>,
	pub essence_type: Option<String>,
	pub amount: Option<u32>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub enum UpgradeType {
	Item,
	Essence,
	Coins,
	Pelts,
	Motes,
	JacobMedal,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct Coordinates {
	pub x: f64,
	pub y: f64,
	pub z: f64,
}
