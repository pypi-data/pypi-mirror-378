use std::collections::HashMap;

#[cfg(feature = "python")]
use pyo3::{pyclass, pymethods};
#[cfg(feature = "python")]
use skyblock_repo_macros::PyStr;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::models::recipe::SkyblockRecipe;

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct SkyblockItem {
	#[serde(default)]
	pub internal_id: String,
	pub name: Option<String>,
	pub category: Option<String>,
	pub source: Option<String>,
	pub npc_value: Option<f64>,
	pub lore: Option<String>,
	pub flags: Option<ItemFlags>,
	/// Hypixel item data from /resources/skyblock/items
	pub data: Option<ItemResponse>,
	pub template_data: Option<ItemTemplate>,
	#[serde(default)]
	pub recipes: Vec<SkyblockRecipe>,
}

#[derive(Debug, Serialize, Deserialize, Default, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct ItemFlags {
	pub tradable: bool,
	pub bazaarable: bool,
	pub auctionable: bool,
	pub reforgeable: bool,
	pub enchantable: bool,
	pub museumable: bool,
	pub soulboundable: bool,
	pub sackable: bool,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct ItemResponse {
	pub id: Option<String>,
	pub material: Option<String>,
	/// formatted as `R,G,B`
	pub color: Option<String>,
	pub durability: Option<i32>,
	pub skin: Option<ItemSkin>,
	pub name: Option<String>,
	pub category: Option<String>,
	pub tier: Option<String>,
	#[serde(default)]
	pub unstackable: bool,
	#[serde(default)]
	pub glowing: bool,
	pub npc_sell_price: Option<f64>,
	#[serde(default)]
	pub can_auction: bool,
	#[serde(default)]
	pub can_trade: bool,
	#[serde(default)]
	pub can_place: bool,
	#[serde(default)]
	pub gemstone_slots: Vec<ItemGemstoneSlot>,
	#[serde(default)]
	pub requirements: Vec<ItemRequirement>,
	#[serde(default)]
	pub museum: bool,
	pub museum_data: Option<ItemMuseumData>,
	pub stats: Option<std::collections::HashMap<String, f64>>,
	pub generator_tier: Option<i32>,
	pub dungeon_item_conversion_cost: Option<DungeonItemConversionCost>,
	#[serde(default)]
	pub upgrade_costs: Vec<Vec<UpgradeCosts>>,
	#[serde(default)]
	pub catacombs_requirements: Vec<CatacombsRequirements>,
	#[serde(default)]
	pub hide_from_viewrecipe_command: bool,
	#[serde(default)]
	pub salvagable_from_recipe: bool,
	pub item_specific: Option<Value>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct ItemSkin {
	pub value: Option<String>,
	pub signature: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct ItemGemstoneSlot {
	pub slot_type: Option<String>,
	#[serde(default)]
	pub costs: Vec<ItemGemstoneSlotCosts>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct ItemGemstoneSlotCosts {
	pub r#type: ItemGemstoneSlotCostsType,
	pub item_id: Option<String>,
	pub coins: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub enum ItemGemstoneSlotCostsType {
	Coins,
	Item,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct ItemRequirement {
	pub r#type: String,
	pub skill: Option<String>,
	pub level: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct ItemMuseumData {
	pub donation_xp: i32,
	#[serde(default)]
	pub parent: HashMap<String, String>,
	pub r#type: Option<String>,
	pub armor_set_donation_xp: Option<HashMap<String, i32>>,
	pub game_stage: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct DungeonItemConversionCost {
	pub essence_type: Option<String>,
	pub amount: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct UpgradeCosts {
	pub r#type: Option<String>,
	pub essence_type: Option<String>,
	pub item_id: Option<String>,
	pub amount: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct CatacombsRequirements {
	pub r#type: Option<String>,
	pub dungeon_type: Option<String>,
	pub level: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct ItemTemplate {
	pub name: Option<String>,
	pub tradable: Option<String>,
	pub auctionable: Option<String>,
	pub bazaarable: Option<String>,
	pub enchantable: Option<String>,
	pub museumable: Option<String>,
	pub reforgeable: Option<String>,
	pub soulboundable: Option<String>,
	pub sackable: Option<String>,
	pub category: Option<String>,
	pub lore: Option<String>,
}
