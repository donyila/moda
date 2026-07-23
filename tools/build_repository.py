#!/usr/bin/env python3
import hashlib,os,zipfile,xml.etree.ElementTree as ET
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
ZIPROOT=os.path.join(ROOT,"zips")
SKIP={".git",".github","tools","zips","__pycache__"}
def addons():
  for n in sorted(os.listdir(ROOT)):
    p=os.path.join(ROOT,n)
    if os.path.isdir(p) and n not in SKIP and os.path.exists(os.path.join(p,"addon.xml")):
      yield n,p,os.path.join(p,"addon.xml")
def version(ax): return ET.parse(ax).getroot().attrib["version"]
def build_zip(name,path,ver):
  outdir=os.path.join(ZIPROOT,name);os.makedirs(outdir,exist_ok=True)
  zpath=os.path.join(outdir,f"{name}-{ver}.zip")
  with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
    for r,ds,fs in os.walk(path):
      ds[:]=[d for d in ds if d!="__pycache__"]
      for f in fs:
        if f.endswith((".pyc",".pyo")): continue
        fp=os.path.join(r,f);arc=os.path.join(name,os.path.relpath(fp,path));z.write(fp,arc)
def build_addons(xmls):
  out=os.path.join(ROOT,"addons.xml")
  with open(out,"w",encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<addons>\n')
    for ax in xmls:
      t=open(ax,encoding="utf-8").read().replace('<?xml version="1.0" encoding="UTF-8"?>','').strip()
      f.write(t+"\n")
    f.write("</addons>\n")
  open(os.path.join(ROOT,"addons.xml.md5"),"w").write(hashlib.md5(open(out,"rb").read()).hexdigest())
def main():
  os.makedirs(ZIPROOT,exist_ok=True);xmls=[]
  for n,p,a in addons():
    build_zip(n,p,version(a));xmls.append(a)
  build_addons(xmls);print("Done")
if __name__=="__main__": main()
