import AnDson_personal_api as AnDson


database = AnDson.Database()
database.create_anime("世界最強",("最強","最強1"),("hs",))
anime1 = database.get_anime("最強1")
anime1_ = database.get_anime("世界最強")
anime2 = database.create_anime("世界最強2",("最強2",),("hs",))



print(database.get_all_animes())