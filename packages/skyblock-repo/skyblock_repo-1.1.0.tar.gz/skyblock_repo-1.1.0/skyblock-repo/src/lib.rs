pub mod models;
mod utils;

use std::collections::HashMap;
use std::fs;
use std::path::Path;

#[cfg(all(feature = "log", not(feature = "python")))]
use log::{trace, warn};
use models::enchantment::SkyblockEnchantment;
use models::item::SkyblockItem;
use models::npc::SkyblockNpc;
use models::pet::SkyblockPet;
use models::shop::SkyblockShop;
use models::zone::SkyblockZone;
pub use models::{UpgradeCost, UpgradeType, enchantment, item, pet, recipe};
#[cfg(feature = "python")]
use pyo3::exceptions::PyValueError;
#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use pyo3::types::PyModule;
use rustc_hash::FxHashMap;
use serde::Deserialize;
#[cfg(not(feature = "python"))]
use skyblock_repo_macros::getter;
pub use utils::{delete_repo, download_repo};

#[cfg(feature = "python")]
#[pymodule]
fn skyblock_repo(m: &Bound<'_, PyModule>) -> PyResult<()> {
	m.add_class::<SkyblockRepo>()?;
	m.add_function(pyo3::wrap_pyfunction!(download_repo, m)?)?;
	m.add_function(pyo3::wrap_pyfunction!(delete_repo, m)?)?;

	Ok(())
}

#[derive(Deserialize)]
struct RepoStructure {
	#[allow(dead_code)]
	version: u8,
	paths: HashMap<String, String>,
}

/// each category of items as a mapping of `internal_id` to its item data
#[cfg_attr(feature = "python", pyclass)]
pub struct SkyblockRepo {
	pub enchantments: FxHashMap<String, SkyblockEnchantment>,
	pub items: FxHashMap<String, SkyblockItem>,
	pub npcs: FxHashMap<String, SkyblockNpc>,
	pub pets: FxHashMap<String, SkyblockPet>,
	pub shops: FxHashMap<String, SkyblockShop>,
	pub zones: FxHashMap<String, SkyblockZone>,
}

#[cfg(feature = "python")]
#[pymethods]
impl SkyblockRepo {
	/// Creates HashMaps for each category
	///
	/// Throws warning log if it encounters a category it did not expect
	///
	/// Requires that the `SkyblockRepo` directory exists, which you can create via
	///
	/// ```rust
	/// skyblock_repo::download_repo(true);
	/// ```
	#[must_use]
	#[new]
	pub fn new() -> PyResult<Self> {
		let structure: RepoStructure =
			serde_json::from_str(&fs::read_to_string("SkyblockRepo/manifest.json")?)
				.map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))?;

		let mut repo = Self {
			enchantments: FxHashMap::default(),
			items: FxHashMap::default(),
			npcs: FxHashMap::default(),
			pets: FxHashMap::default(),
			shops: FxHashMap::default(),
			zones: FxHashMap::default(),
		};

		for path_name in structure.paths.values() {
			let path = &format!("SkyblockRepo/{}", path_name);
			let path = Path::new(path);
			let data_entries = fs::read_dir(&path)?;

			for json in data_entries {
				let json = json?.path();
				let content = fs::read_to_string(&json)?;

				match path_name.as_str() {
					| "enchantments" => {
						let parsed: SkyblockEnchantment = serde_json::from_str(&content)
							.map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))?;
						repo.enchantments.insert(parsed.internal_id.clone(), parsed);
					},
					| "items" => {
						let parsed: SkyblockItem = serde_json::from_str(&content)
							.map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))?;
						repo.items.insert(parsed.internal_id.clone(), parsed);
					},
					| "npcs" => {
						let parsed: SkyblockNpc = serde_json::from_str(&content)
							.map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))?;
						repo.npcs.insert(parsed.internal_id.clone(), parsed);
					},
					| "pets" => {
						let parsed: SkyblockPet = serde_json::from_str(&content)
							.map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))?;
						repo.pets.insert(parsed.internal_id.clone(), parsed);
					},
					| "shops" => {
						let parsed: SkyblockShop = serde_json::from_str(&content)
							.map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))?;
						repo.shops.insert(parsed.internal_id.clone(), parsed);
					},
					| "zones" => {
						let parsed: SkyblockZone = serde_json::from_str(&content)
							.map_err(|e| PyErr::new::<PyValueError, _>(e.to_string()))?;
						repo.zones.insert(parsed.internal_id.clone(), parsed);
					},
					| _ => continue,
				}
			}
		}

		Ok(repo)
	}

	/// Retrieves an enchantment by its `internalId`
	#[must_use]
	#[inline]
	pub fn get_enchantment_by_id(
		&self,
		id: &str,
	) -> Option<SkyblockEnchantment> {
		self.enchantments.get(&id.to_uppercase()).cloned()
	}

	/// Retrieves an item by its `internalId`
	#[must_use]
	#[inline]
	pub fn get_item_by_id(
		&self,
		id: &str,
	) -> Option<SkyblockItem> {
		self.items.get(&id.to_uppercase()).cloned()
	}

	/// Retrieves an npc by its `internalId`
	#[must_use]
	#[inline]
	pub fn get_npc_by_id(
		&self,
		id: &str,
	) -> Option<SkyblockNpc> {
		self.npcs.get(&id.to_uppercase()).cloned()
	}

	/// Retrieves a pet by its `internalId`
	#[must_use]
	#[inline]
	pub fn get_pet_by_id(
		&self,
		id: &str,
	) -> Option<SkyblockPet> {
		self.pets.get(&id.to_uppercase()).cloned()
	}

	/// Retrieves a shop by its `internalId`
	#[must_use]
	#[inline]
	pub fn get_shop_by_id(
		&self,
		id: &str,
	) -> Option<SkyblockShop> {
		self.shops.get(&id.to_uppercase()).cloned()
	}

	/// Retrieves a zone by its `internalId`
	#[must_use]
	#[inline]
	pub fn get_zone_by_id(
		&self,
		id: &str,
	) -> Option<SkyblockZone> {
		self.zones.get(&id.to_uppercase()).cloned()
	}
}

#[cfg(not(feature = "python"))]
impl SkyblockRepo {
	pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
		let structure: RepoStructure =
			serde_json::from_str(&fs::read_to_string("SkyblockRepo/manifest.json")?)?;

		let mut repo = Self {
			enchantments: FxHashMap::default(),
			items: FxHashMap::default(),
			npcs: FxHashMap::default(),
			pets: FxHashMap::default(),
			shops: FxHashMap::default(),
			zones: FxHashMap::default(),
		};

		for path_name in structure.paths.values() {
			let path = &format!("SkyblockRepo/{}", path_name);
			let path = Path::new(path);
			let data_entries = fs::read_dir(&path)?;

			for json in data_entries {
				let json = json?.path();
				#[cfg(feature = "log")]
				trace!("parsing {:?}", json);
				let content = fs::read_to_string(&json)?;

				match path_name.as_str() {
					| "enchantments" => {
						let parsed: SkyblockEnchantment = serde_json::from_str(&content)?;
						repo.enchantments.insert(parsed.internal_id.clone(), parsed);
					},
					| "items" => {
						let parsed: SkyblockItem = serde_json::from_str(&content)?;
						repo.items.insert(parsed.internal_id.clone(), parsed);
					},
					| "npcs" => {
						let parsed: SkyblockNpc = serde_json::from_str(&content)?;
						repo.npcs.insert(parsed.internal_id.clone(), parsed);
					},
					| "pets" => {
						let parsed: SkyblockPet = serde_json::from_str(&content)?;
						repo.pets.insert(parsed.internal_id.clone(), parsed);
					},
					| "shops" => {
						let parsed: SkyblockShop = serde_json::from_str(&content)?;
						repo.shops.insert(parsed.internal_id.clone(), parsed);
					},
					| "zones" => {
						let parsed: SkyblockZone = serde_json::from_str(&content)?;
						repo.zones.insert(parsed.internal_id.clone(), parsed);
					},
					#[cfg_attr(not(feature = "log"), allow(unused_variables))]
					| other => {
						#[cfg(feature = "log")]
						warn!("Unknown dir found while parsing SkyblockData: {}", other);
						continue;
					},
				}
			}
		}

		Ok(repo)
	}

	getter!(enchantment);
	getter!(item);
	getter!(pet);
	getter!(npc);
	getter!(shop);
	getter!(zone);
}
