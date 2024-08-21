import os

    
# getting size of zarr folder recursively 
def folder_size(folder_path: str) -> str:
    def convert_bytes(B: int) -> str:
        """Return the given bytes as a human friendly KB, MB, GB, or TB string."""
        B = float(B)
        KB = float(1000) # change to 1024 for non mac file systems 
        MB = float(KB ** 2) # 1,048,576
        GB = float(KB ** 3) # 1,073,741,824
        TB = float(KB ** 4) # 1,099,511,627,776

        if B < KB:
            return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
        elif KB <= B < MB:
            return '{0:.2f} KB'.format(B / KB)
        elif MB <= B < GB:
            return '{0:.2f} MB'.format(B / MB)
        elif GB <= B < TB:
            return '{0:.2f} GB'.format(B / GB)
        elif TB <= B:
            return '{0:.2f} TB'.format(B / TB)
    
    def get_folder_size(folder: str) -> int:
        total_size = os.path.getsize(folder)
        
        for item in os.listdir(folder):
            item_path = os.path.join(folder, item)
            
            if os.path.isfile(item_path):
                total_size += os.path.getsize(item_path)
            elif os.path.isdir(item_path):
                total_size += get_folder_size(item_path)
                
        return total_size
    
    size = get_folder_size(folder = folder_path)
    formatted_size = convert_bytes(B = size)
    
    return formatted_size
    