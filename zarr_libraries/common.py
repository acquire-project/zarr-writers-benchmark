import napari
import dask.array as da
import os


# viewing data with napari
def view_zarr(folder_path: str) -> None:
    data = da.from_zarr(folder_path)
    napari.view_image(data, colormap='magma')
    napari.run()
   
    
# getting size of zarr folder recursively 
def folder_size(folder_path: str) -> None:
    def getFolderSize(folder: str) -> int:
        total_size = os.path.getsize(folder)
        
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            
            if os.path.isfile(item_path):
                total_size += os.path.getsize(item_path)
            elif os.path.isdir(item_path):
                total_size += getFolderSize(item_path)
                
        return total_size
    
    print("The zarr folder is of size " + str(getFolderSize(folder_path)) + " bytes\n\n")
    