mod repo;

#[cfg(feature = "python")]
pub use repo::python::{delete_repo_files as delete_repo, download_zip as download_repo};
#[cfg(not(feature = "python"))]
pub use repo::rust::{delete_repo_files as delete_repo, download_zip as download_repo};
