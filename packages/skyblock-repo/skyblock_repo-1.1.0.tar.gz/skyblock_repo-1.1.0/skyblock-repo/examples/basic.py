#!/usr/bin/env python3
from skyblock_repo import download_repo, delete_repo, SkyblockRepo

def main():
	download_repo(True)

	repo = SkyblockRepo()

	print(repo.get_enchantment_by_id("TELEKINESIS"))

	delete_repo()

if __name__ == "__main__":
	main()
