use std::time::Instant;

use skyblock_repo::{SkyblockRepo, delete_repo, download_repo};

fn main() {
	let mut start = Instant::now();
	download_repo(false, None).unwrap();
	println!(
		"Time taken to download and extract repo: {}s",
		start.elapsed().as_secs_f32()
	);
	start = Instant::now();

	let data = SkyblockRepo::new().unwrap();
	println!(
		"Time taken to parse repo: {}ms",
		start.elapsed().as_millis()
	);
	start = Instant::now();

	println!("{:?}", data.get_enchantment_by_id("TELEKINESIS"));
	println!(
		"Time taken to get data for `TELEKINESIS`: {}µs",
		(start.elapsed().as_nanos() as f32 / 1_000.0)
	);
	start = Instant::now();

	delete_repo().unwrap();
	println!(
		"Time taken to delete repo: {}ms",
		start.elapsed().as_millis()
	);
}
