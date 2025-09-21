#[cfg(feature = "python")]
pub mod python {
	use std::fs::{File, OpenOptions, create_dir_all, exists, remove_dir_all, remove_file, rename};
	use std::io::{self, Write};
	use std::path::Path;

	use pyo3::exceptions::{PyIOError, PyRuntimeError};
	use pyo3::*;

	/// Downloads the github SkyblockRepo data and unzips
	#[pyfunction(name = "download_repo")]
	#[pyo3(signature=(delete_zip=true, commit="main"))]
	pub fn download_zip(
		delete_zip: bool,
		commit: &str,
	) -> PyResult<()> {
		let url = format!(
			"https://github.com/SkyblockRepo/Repo/archive/{}.zip",
			commit
		);

		let mut response = ureq::get(url)
			.call()
			.map_err(|e| PyErr::new::<PyRuntimeError, _>(e.to_string()))?;

		if !exists("SkyblockRepo")? || (!exists("SkyblockRepo.zip")? && !exists("SkyblockRepo")?) {
			if response.status() == 200 {
				let mut file = OpenOptions::new()
					.read(true)
					.write(true)
					.create_new(true)
					.open("SkyblockRepo.zip")?;

				let content = response
					.body_mut()
					.read_to_vec()
					.map_err(|e| PyErr::new::<PyRuntimeError, _>(e.to_string()))?;
				file.write_all(&content)?;

				unzip_repo(file, commit)?;
			} else {
				return Err(PyErr::new::<PyRuntimeError, _>(format!(
					"Reqwest failed with status {}",
					response.status()
				)));
			}
		} else {
			return Ok(());
		}

		if delete_zip {
			remove_file(Path::new("SkyblockRepo.zip"))?;
		}

		Ok(())
	}

	fn unzip_repo(
		file: File,
		commit: &str,
	) -> PyResult<()> {
		let mut archive =
			zip::ZipArchive::new(file).map_err(|e| PyErr::new::<PyIOError, _>(e.to_string()))?;

		for i in 0..archive.len() {
			let mut file = archive
				.by_index(i)
				.map_err(|e| PyErr::new::<PyIOError, _>(e.to_string()))?;
			let outpath = match file.enclosed_name() {
				| Some(path) => path,
				| None => continue,
			};

			if file.is_dir() {
				create_dir_all(&outpath)?;
			} else {
				if let Some(p) = outpath.parent() {
					if !p.exists() {
						create_dir_all(p)?;
					}
				}
				let mut outfile = File::create(&outpath)?;
				io::copy(&mut file, &mut outfile)?;
			}

			#[cfg(unix)]
			{
				use std::os::unix::fs::PermissionsExt;

				if let Some(mode) = file.unix_mode() {
					use std::fs::{Permissions, set_permissions};

					set_permissions(&outpath, Permissions::from_mode(mode))?;
				}
			}
		}

		rename(
			Path::new(&format!("Repo-{}", commit)),
			Path::new("SkyblockRepo"),
		)?;

		Ok(())
	}

	#[pyfunction(name = "delete_repo")]
	pub fn delete_repo_files() -> PyResult<()> {
		let _ = remove_file("SkyblockRepo.zip").or_else(|err| {
			// stifle file not found error because you can already remove the zip in the download function
			if err.kind() == io::ErrorKind::NotFound {
				Ok(())
			} else {
				Err(err)
			}
		})?;
		remove_dir_all("SkyblockRepo")?;
		Ok(())
	}
}

#[cfg(not(feature = "python"))]
pub mod rust {
	use std::fs::{File, OpenOptions, create_dir_all, exists, remove_dir_all, remove_file, rename};
	use std::io::{self, Write};
	use std::path::Path;

	#[cfg(feature = "log")]
	use log::{error, trace};

	/// Downloads the github SkyblockRepo data and unzips
	///
	/// You can additonally remove the downloaded zip and only keep the extracted directory by passing in `true`
	pub fn download_zip(
		delete_zip: bool,
		commit: Option<&str>,
	) -> Result<(), Box<dyn std::error::Error>> {
		let commit = commit.unwrap_or("main");
		let url = format!(
			"https://github.com/SkyblockRepo/Repo/archive/{}.zip",
			commit
		);

		let mut response = ureq::get(url).call()?;

		if !exists("SkyblockRepo")? || (!exists("SkyblockRepo.zip")? && !exists("SkyblockRepo")?) {
			if response.status() == 200 {
				let mut file = OpenOptions::new()
					.read(true)
					.write(true)
					.create_new(true)
					.open("SkyblockRepo.zip")?;

				let content = response.body_mut().read_to_vec()?;
				file.write_all(&content)?;

				unzip_repo(file, commit)?;
			} else {
				return Err(format!("Reqwest failed with status {}", response.status()).into());
			}
		} else {
			#[cfg(feature = "log")]
			error!(
				"SkyblockRepo.zip and/or SkyblockRepo/ directory are present, if you wish to refetch them, delete them."
			);
			return Ok(());
		}

		if delete_zip {
			remove_file(Path::new("SkyblockRepo.zip"))?;
		}

		Ok(())
	}

	fn unzip_repo(
		file: File,
		commit: &str,
	) -> Result<(), Box<dyn std::error::Error>> {
		let mut archive = zip::ZipArchive::new(file)?;

		for i in 0..archive.len() {
			let mut file = archive.by_index(i)?;
			let outpath = match file.enclosed_name() {
				| Some(path) => path,
				| None => continue,
			};

			if file.is_dir() {
				#[cfg(feature = "log")]
				trace!("File {} extracted to \"{}\"", i, outpath.display());
				create_dir_all(&outpath)?;
			} else {
				#[cfg(feature = "log")]
				trace!(
					"File {} extracted to \"{}\" ({} bytes)",
					i,
					outpath.display(),
					file.size()
				);
				if let Some(p) = outpath.parent() {
					if !p.exists() {
						create_dir_all(p)?;
					}
				}
				let mut outfile = File::create(&outpath)?;
				io::copy(&mut file, &mut outfile)?;
			}

			#[cfg(unix)]
			{
				use std::os::unix::fs::PermissionsExt;

				if let Some(mode) = file.unix_mode() {
					use std::fs::{Permissions, set_permissions};

					set_permissions(&outpath, Permissions::from_mode(mode))?;
				}
			}
		}

		rename(
			Path::new(&format!("Repo-{}", commit)),
			Path::new("SkyblockRepo"),
		)?;

		Ok(())
	}

	pub fn delete_repo_files() -> Result<(), Box<dyn std::error::Error>> {
		let _ = remove_file("SkyblockRepo.zip").or_else(|err| {
			// stifle file not found error because you can already remove the zip in the download function
			if err.kind() == io::ErrorKind::NotFound {
				Ok(())
			} else {
				Err(err)
			}
		})?;
		remove_dir_all("SkyblockRepo")?;
		Ok(())
	}
}
