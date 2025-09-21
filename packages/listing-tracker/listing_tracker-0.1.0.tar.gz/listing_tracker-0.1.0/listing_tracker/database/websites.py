from listing_tracker.database import classes

website_list = classes.Table("websites")
website_list.column_assign([classes.Column("name", "text", False, ""), classes.Column("domain", "text", False, "")])
website_list_dict = website_list.get_dict()
if not website_list.exists():
    website_list.create(website_list_dict)
    website_list_values: list[tuple] = [("[COM] Amazon", "www.amazon.com"),
        ("[JP] Amazon", "www.amazon.co.jp"), ("eBay", "www.ebay.com"),
        ("Lashinbang", "shop.lashinbang.com"), ("Mandarake", "www.mandarake.co.jp"),
        ("[JP] Mercari", "jp.mercari.com"), ("[JP] Mercari", "mercari.jp"),
        ("[COM] Mercari", "www.mercari.com")]
    website_list.insert_many(website_list_values)