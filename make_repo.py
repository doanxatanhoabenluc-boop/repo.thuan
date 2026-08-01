import os
import glob
import struct

def extract_control_from_deb(deb_path):
    """Trích xuất file control bằng cách đọc cấu trúc ar & tar bằng Python thuần."""
    try:
        with open(deb_path, 'rb') as f:
            magic = f.read(8)
            if magic != b'!<arch>\n':
                return None
            
            # Đọc từng header trong file ar
            while True:
                header = f.read(60)
                if not header or len(header) < 60:
                    break
                
                # Cấu trúc header ar: name(16), mtime(12), owner(6), group(6), mode(8), size(10), fmag(2)
                file_name = header[:16].decode('ascii', errors='ignore').strip()
                file_size = int(header[48:58].decode('ascii', errors='ignore').strip())
                
                # Đọc dữ liệu của subfile này
                data = f.read(file_size)
                if file_size % 2 != 0:
                    f.read(1) # Padding byte nếu kích thước lẻ
                
                # Nếu tìm thấy control archive (control.tar.gz / control.tar.xz / control.tar)
                if 'control.tar' in file_name:
                    import io, tarfile
                    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
                        for member in tar.getmembers():
                            if member.name.endswith('control'):
                                control_file = tar.extractfile(member)
                                if control_file:
                                    return control_file.read().decode('utf-8', errors='ignore').strip()
    except Exception as e:
        return None
    return None

def main():
    debs = glob.glob("debs/*.deb")
    if not debs:
        print("Không tìm thấy file .deb nào trong thư mục debs!")
        return

    packages = []
    print(f"Đang quét {len(debs)} file deb...")

    for deb in debs:
        filename = os.path.basename(deb)
        control = extract_control_from_deb(deb)
        
        if control:
            # Tự động gắn đường dẫn Filename chuẩn cho Cydia Repo
            entry = control + f"\nFilename: debs/{filename}"
            packages.append(entry)
            print(f" Thành công: {filename}")
        else:
            print(f"❌ Bỏ qua: {filename}")

    # Ghi ra file Packages
    with open("Packages", "w", encoding="utf-8") as f:
        f.write("\n\n".join(packages) + "\n")

    print("\n==========================================")
    print("===> XONG! Đã tạo thành công file Packages!")
    print("==========================================")

if __name__ == '__main__':
    main()