use std::collections::HashMap;

#[cfg(feature = "python")]
use pyo3::{pyclass, pymethods};
use serde::{Deserialize, Serialize};
#[cfg(feature = "python")]
use skyblock_repo_macros::PyStr;

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct SkyblockRecipe {
	pub name: Option<String>,
	pub r#type: RecipeType,
	pub result_id: Option<String>,
	pub result_quantity: i32,
	pub crafting: HashMap<String, RecipeIngredient>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub struct RecipeIngredient {
	pub item_id: String,
	pub quantity: i32,
}

#[derive(Debug, Serialize, Deserialize, Default, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
#[cfg_attr(feature = "python", pyclass, derive(PyStr))]
pub enum RecipeType {
	#[default]
	Crafting,
}
