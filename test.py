import AnDson_personal_api as AnDson


database = AnDson.Database("AnDson_personal.json")
database.create_anime("世界最強",("最強","最強1"),("hs",))
anime1 = database.get_anime("最強1")
anime1_ = database.get_anime("世界最強")
anime2 = database.create_anime("世界最強2",("最強2",),("hs",))

print(anime1 == anime1_)
print(anime1 is anime1_)


print(database._raw_dict)