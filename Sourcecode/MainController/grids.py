import numpy as np
from settings import Side

def create_table_cluster(table_section, cropped=True, np_arr=True):
    def fill_cluster(cluster, table_section, x=0, y=0, flipped=False):   
        # Add Table Section to cluster and its neighbors to the cluster, then build through neighbors
        # Skip known Table Sections in cluster
        if any(table_section in row for row in cluster):
            return

        cluster[y][x] = table_section

        for side, neighbor in table_section.get_neighbors().iteritems():
            if neighbor is None:
                continue

            # Temp flip sides
            grid_side = Side.flip_side(side) if flipped else side
            n_y = y
            n_x = x

            if grid_side is Side.NORTH:
                n_y -= 1
            if grid_side is Side.EAST:
                n_x += 1
            if grid_side is Side.SOUTH:
                n_y += 1
            if grid_side is Side.WEST:
                n_x -= 1

            #  is neighbor flipped?
            neighbor_flipped = ((neighbor.get_neighbors()[side] is table_section) is not flipped)
            fill_cluster(cluster, neighbor, x=n_x, y=n_y, flipped=neighbor_flipped)


    # create a new array for this table cluster, 11 x 11, starting at center
    table_cluster = [[0 for x in range(11)] for y in range(11)]
    fill_cluster(table_cluster, table_section, x=5, y=5)

    if cropped:
        # Crop cluster
        table_cluster = np.array(table_cluster)
        table_cluster = crop_array(table_cluster)
        if not np_arr:
            # Convert back to normal array
            table_cluster = np.ndarray.tolist(table_cluster) 

    return table_cluster 



def fill_grid_with_cluster(grid, cluster, start_x, start_y):
    for (y,x), value in np.ndenumerate(cluster):
        grid[start_y + y][start_x + x] = value

def crop_array(array, crop_val=0, min_x=1, min_y=1):
    # Cropping 2d array, taken from https://stackoverflow.com/a/34731073
    mask = array == crop_val
    rows = np.flatnonzero((~mask).sum(axis=1))
    cols = np.flatnonzero((~mask).sum(axis=0))
    offset_x = 1
    offset_y = 1
    if ((rows.max() + 1) - rows.min()) < min_y: 
        offset_y = min_y
    if ((cols.max() + 1) - cols.min()) < min_x: 
        offset_x = min_x
    cropped_array = array[rows.min():rows.max()+offset_y, cols.min():cols.max()+offset_x]
    return cropped_array