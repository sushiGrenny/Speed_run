   for y, row in enumerate(world_data):
        for x, tiles in enumerate(row):
            if tiles >=0:
                screen.blit(img_list[tiles],(x * Tile_size - scroll, y * Tile_size))