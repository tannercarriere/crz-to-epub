import zipfile
from epub_writer import EpubWriter
from shutil import copyfile
from os import path, mkdir

def main():
    print("||| CRZ to EPUB |||")
    crz_in  = input("crz file: ")
    copyfile(crz_in, "tmp_crz.zip")

    epub = EpubWriter(path.basename(crz_in)[0:-4], crz_in[0:-4] + ".opf")
    epub.define_file_structure()
    with zipfile.ZipFile("tmp_crz.zip") as crz:
        epub.add_images(crz)
        crz.close()
    epub.create_metadata()
    epub.gen_pages()


if __name__ == '__main__':
    main()