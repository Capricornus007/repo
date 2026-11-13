#!/usr/bin/env python3
"""把 YouTube APK 的 versionName 從 21.46.520-BETA 改成 21.46.520（純數字）。

直接改 binary AndroidManifest.xml 的 string pool：新字串較短，原地覆寫並更新
length 欄位，其餘字串 offset 不受影響。

用法: fix_youtube_version.py <src.apk> <dst.apk>
"""
import zipfile, struct, sys

OLD = '21.46.520-BETA'
NEW = '21.46.520'

def main():
    src, dst = sys.argv[1], sys.argv[2]
    with zipfile.ZipFile(src) as z:
        data = bytearray(z.read('AndroidManifest.xml'))

    type_, hsize, size = struct.unpack_from('<HHI', data, 0)
    assert type_ == 0x0003
    off = hsize
    type_, hsize2, size2 = struct.unpack_from('<HHI', data, off)
    assert type_ == 0x0001, 'first chunk is not string pool'
    stringCount, styleCount, flags, stringsStart, stylesStart = struct.unpack_from('<IIIII', data, off + 8)
    assert not (flags & 0x100), 'expected UTF-16 string pool'
    offsets_pos = off + hsize2
    string_data_pos = off + stringsStart

    def read_u16_string(pos):
        first = struct.unpack_from('<H', data, pos)[0]
        if first & 0x8000:
            length = ((first & 0x7FFF) << 16) | struct.unpack_from('<H', data, pos + 2)[0]
            hdr = 4
        else:
            length = first
            hdr = 2
        raw = data[pos + hdr: pos + hdr + length * 2]
        return length, hdr, raw.decode('utf-16-le')

    replaced = 0
    for i in range(stringCount):
        soff = struct.unpack_from('<I', data, offsets_pos + i * 4)[0]
        pos = string_data_pos + soff
        length, hdr, s = read_u16_string(pos)
        if s == OLD:
            new_bytes = NEW.encode('utf-16-le')
            struct.pack_into('<H', data, pos, len(NEW))
            data[pos + 2: pos + 2 + len(new_bytes)] = new_bytes
            struct.pack_into('<H', data, pos + 2 + len(new_bytes), 0)
            replaced += 1
            print('replaced string #%d at pool offset %d' % (i, soff))

    print('total replaced:', replaced)
    assert replaced >= 1, 'versionName string not found'

    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            buf = zin.read(item.filename)
            if item.filename == 'AndroidManifest.xml':
                buf = bytes(data)
            zout.writestr(item, buf)
    print('written:', dst)

if __name__ == '__main__':
    main()
