from listing_tracker.database import listings
import sys

add_listing = listings.add_listing
listings_table = listings.listings_table

if __name__ == "__main__" and len(sys.argv) >= 3:
    add_cmd = sys.argv[1] == "add"
    listing_arg = sys.argv[2] == "listing"
    items_args = sys.argv[3:]
    if add_cmd and listing_arg and items_args:
        for url in items_args:
            add_listing(listings_table, url)