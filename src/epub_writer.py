from os import mkdir, path
from shutil import copyfile
from glob import glob
import xml.etree.ElementTree as ET

class EpubWriter:
    def __init__(self, name, opf_file=None):
        self.name = name
        self.opf_file = opf_file

    def define_file_structure(self):
        mkdir(self.name)
        mkdir(self.name + "/item")
        mkdir(self.name + "/item/image")
        mkdir(self.name + "/item/style")
        mkdir(self.name + "/item/xhtml")
        mkdir(self.name + "/META-INF")

    def add_images(self, crz):
        crz.extractall(self.name + "/item/image")

    def create_metadata(self, opf_file=None):
        f = open(self.name +"/mimetype", "w")
        f.write("application/epub+zip")
        f.close()
        #TODO: META-INF
        uuid = None
        if self.opf_file:
            copyfile(self.opf_file, self.name + "/item/tmp.xml")
            meta_data = ET.parse(self.name + "/item/tmp.xml") # TODO: clean up tmp file
            package = meta_data.getroot()
            manifest = ET.SubElement(package, "manifest")
            spine = ET.SubElement(package, "spine", {"page-progression-direction":"ltr"})
            page_number = 1
            page_string = f"p_{page_number:03d}"
            images = [path.basename(x) for x in glob(self.name+"/item/image/*")]
            for image in images:
                ET.SubElement(manifest, "item", {"media-type":"image/jpeg", "id":image, "href":"image/"+image})
                ET.SubElement(manifest, "item", {"media-type":"application/xhtml+xml", "id":page_string, "href":"xhtml/"+page_string})
                ET.SubElement(spine, "itemref", {"linear":"yes", "idref":page_string})
                page_number += 1
                page_string = f"p_{page_number:03d}"
                
            meta_data.write(self.name + "/item/" + self.name + ".opf")
            for tag in meta_data.findall("dc:identifier"):
                if tag["id"] == "uuid_id":
                    uuid = tag.text
                    break

        else:
            print(".opf file not found")
            return
        
        ncx_tree = ET.ElementTree()
        ncx = ET.Element("ncx", {"version":"2005-1", "xml:lang":"en", "xmlns":"http://www.daisy.org/z3986/2005/ncx/"})
        head = ET.SubElement(ncx, "head")
        ET.SubElement(head, "meta", {"name":"dtb:uid", "content":str(uuid)})
        ET.SubElement(head, "meta", {"name":"dtb:depth", "content":"1"})
        ET.SubElement(head, "meta", {"name":"dtb:totalPageCount", "content":"0"})
        ET.SubElement(head, "meta", {"name":"dtb:maxPageNumber", "content":"0"})
        doc_title = ET.SubElement(ncx, "docTitle")
        ET.SubElement(doc_title, "text").text = self.name
        ncx_tree._setroot(ncx)
        ncx_tree.write(self.name + "/item/toc.ncx")

    def gen_pages(self):
        images = [path.basename(x) for x in glob(self.name+"/item/image/*")]
        cover = images.pop(0)
        header = '<?xml version="1.0" encoding="UTF-8"?>\n'
        header += '<!DOCTYPE html>\n<html\nxmlns="http://www.w3.org/1999/xhtml"'
        header += '\nxmlns:epub="http://www.idpf.org/2007/ops"\nxml:lang="ja"\nclass="hltr"\n>'
        header += f'<head>\n<meta charset="UTF-8"/>\n<title>{self.name}</title>\n'
        header += '<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>\n</head>'

        body = '<body epub:type="cover" class="cover-page">'
        body += f'<div class="main"><p><img class="fit" src="../image/{cover}" alt=""/></p></div>'
        body += '</div></body></html>'
        with open(self.name + "/item/xhtml/p_0001.xhtml", "w") as f:
            f.write(header + body)
        i = 2
        for image in images:
            body = '<body epub:type="cover" class="cover-page">'
            body += f'<div class="main"><p><img class="fit" src="../image/{image}" alt=""/></p></div>'
            body += '</div></body></html>'
            with open(self.name + f"/item/xhtml/p_{i:03d}.xhtml", "w") as f:
                f.write(header + body)
            i += 1

