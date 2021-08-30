#!/usr/bin/env python3

# V. 1.3.3
############
# do not store the file paths after a copy/cut operation: 0 NO - 1 YES
SKIP_FILES = 1
############

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango
from gi.repository.GdkPixbuf import Pixbuf
import os
import sys
from shutil import copyfile
from pathlib import Path
from time import time, sleep
import zlib

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

XALIGN = 1

data = True

main_window = True

pint = 2
tclipb = None
ccdir = os.getcwd()
ccrc = 0
ccrc2 = 0

def cr_history():
    if Path('history.xml').exists() == False:
        try:
            fp = open('history.xml', 'w')
        except FileNotFoundError:
            pass
        else:
            with fp:
                fp.write('<history version="1.0">'+'\n'+'</history>')
                fp.close()

cr_history()

def cr_images():
    if Path('images').exists() == False:
        try:
            os.makedirs('images')
        except OSError:
            pass

cr_images()
images_path = "images/"

clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
clipboard.set_text("", -1)
clipboard.clear()

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Gpasteboard")
        self.connect("destroy", lambda w: self.destroy())
        self.connect("destroy", self.cclose)
        self.set_icon_from_file("clipman.svg")
        self.set_border_width(5)
        self.set_default_size(800, 800)
        self.set_resizable(True)
        self.set_position(1)
        
        self.hbox = Gtk.Box(spacing=10)
        self.hbox.set_homogeneous(False)
        self.add(self.hbox)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.hbox.pack_start(self.grid, False, False, 1)

        self.label1 = Gtk.Label(label="<b>0</b> in history")
        self.label1.set_use_markup(True)
        self.grid.attach(self.label1, 0, 0, 1, 1)
        self.grid.set_row_spacing(30)
        
        self.label0 = Gtk.Label(label="<b>0</b> image(s)")
        self.label0.set_use_markup(True)
        self.grid.attach(self.label0, 0, 1, 1, 1)
      
        self.button1 = Gtk.Button(label="Empty history")
        self.button1.connect("clicked", self.on_empty_clicked)
        self.grid.attach(self.button1, 0, 2, 1, 1)
        
        self.button2 = Gtk.Button(label="Quit")
        self.button2.connect("clicked", lambda w: self.destroy())
        self.button2.connect("clicked", self.cclose)
        self.button2.props.valign = 2
        self.button2.props.vexpand = True
        self.grid.attach(self.button2, 0, 3, 1, 1)
        
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.hbox.pack_start(self.notebook, True, True, 0)
        
        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.notebook.append_page(self.page1, Gtk.Label(label='Text'))

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_placement(Gtk.CornerType.TOP_RIGHT)
        self.page1.add(self.scrolledwindow)     

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.scrolledwindow.add(self.listbox)
       
        aa = []
        cc = []       

        ccdir = os.getcwd()
        
        tree = ET.parse('history.xml')
        root = tree.getroot()
        
        for iitem in root.iter('item'):
            if list(iitem.attrib.values())[0] == 'Text':
                ttext = iitem.text.strip()
                if len(ttext) < 51:
                    aa.append(ttext.replace('\n', " "+u'\u00AC'+" "))
                else:
                    aa.append(ttext[:51].replace('\n', " "+u'\u00AC'+" ")+" [...]")

        os.chdir(images_path)
        aaa = sorted(os.listdir())
        for iitem in aaa[:]:

            if os.path.splitext(iitem)[1] == '.tiff':
                cc.append(iitem)

        os.chdir(ccdir)    

        q = 0   
        iq = 0   

        for iitem in aa:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            row.add(hbox)
            n_label = Gtk.Label(label=XALIGN)
            # n_label.modify_font(Pango.FontDescription.from_string("Mono"))
            label = Gtk.Label(xalign=0)
            label.set_single_line_mode(True)
            n_label.set_text("{0:>3n}.".format(q+1))
            label.set_text(str(iitem))
            button = Gtk.Button()
            iicon = Gio.ThemedIcon(name="list-remove")
            iimage = Gtk.Image.new_from_gicon(iicon, Gtk.IconSize.BUTTON)
            button.add(iimage)
            button.set_tooltip_text("Delete this item.")
            button.connect("clicked", self.on_tdelbutton_clicked, row)
            button2 = Gtk.Button()
            iicon2 = Gio.ThemedIcon(name="document-page-setup")
            iimage2 = Gtk.Image.new_from_gicon(iicon2, Gtk.IconSize.BUTTON)
            button2.add(iimage2)
            button2.set_tooltip_text("Preview.")
            button2.connect("clicked", self.on_preview_dialog, row)
            hbox.pack_start(n_label, False, False, 4)
            hbox.pack_start(label, True, True, 10)
            hbox.pack_start(button2, False, False, 0)
            hbox.pack_start(button, False, False, 0)
            self.listbox.add(row)
            q += 1
        
        for iitem in reversed(cc):
            grid0 = Gtk.Grid(hexpand=True, vexpand=True)
            grid0.set_column_homogeneous(True)
            hbox0 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            button0 = Gtk.Button()
            button0.set_tooltip_text("Copy this image.")
            button0.connect("clicked", self.on_copy_image, cc[:])
            iicon = Gio.ThemedIcon(name="dialog-ok")
            iimage = Gtk.Image.new_from_gicon(iicon, Gtk.IconSize.BUTTON)
            button0.add(iimage)
            pixbuf = Pixbuf.new_from_file("images/"+iitem)
            image = Gtk.Image()
            image.set_hexpand(True)
            image.set_vexpand(True)
            ws_p = Pixbuf.get_width(pixbuf)
            hs_p = Pixbuf.get_height(pixbuf)
            if ws_p > 600 or hs_p > 600:
                if ws_p > hs_p:
                    c_ws_p = 600
                    c_hs_p = hs_p*600/ws_p
                else:
                    c_hs_p = 600
                    c_ws_p = ws_p*600/hs_p
                pixbuf = Pixbuf.scale_simple(pixbuf, c_ws_p, c_hs_p, 2)
            image.set_from_pixbuf(pixbuf)
            button = Gtk.Button()
            iicon = Gio.ThemedIcon(name="list-remove")
            iimage = Gtk.Image.new_from_gicon(iicon, Gtk.IconSize.BUTTON)
            button.add(iimage)
            button.set_tooltip_text("Delete this image.")
            button.connect("clicked", self.on_idelbutton_clicked, cc[:])
            button2 = Gtk.Button()
            iicon2 = Gio.ThemedIcon(name="stock_save")
            iimage2 = Gtk.Image.new_from_gicon(iicon2, Gtk.IconSize.BUTTON)
            button2.add(iimage2)
            button2.set_tooltip_text("Save this image.")
            button2.connect("clicked", self.on_isavebutton_clicked,  cc[:])
            hbox0.pack_start(button0, True, True, 0)
            hbox0.pack_start(button2, True, True, 0)
            hbox0.pack_start(button, True, True, 0)
            grid0.attach(image, 0, 1, 1, 1)
            grid0.attach_next_to(hbox0, image, Gtk.PositionType.BOTTOM, 1, 1)
            page = Gtk.Box()
            page.add(grid0)
            label = Gtk.Label("Image")
            self.notebook.append_page(page, label)
            grid0.show()
            image.show()
            button2.show()
            page.show()
            iq += 1
            global pint
            pint += 1
        
        self.label0.set_text("<b>{}</b> image(s)".format(iq))
        self.label0.set_use_markup(True)
        self.label1.set_text("<b>{}</b> in history".format(q))
        self.label1.set_use_markup(True)
        self.listbox.connect("row-activated", self.on_row_clicked)
        self.show_all()
        self.notebook.set_current_page(0)

    def cclose(self, dat=None):
        global main_window
        main_window = True

    def on_row_clicked2(self, dat = None):
        global data
        sleep(0.1)
        data = True

    def on_row_clicked(self, listbox, listboxrow):
        ii = listboxrow.get_index()
        global tree
        global data
        global tclipb
        tree = ET.parse('history.xml')
        root = tree.getroot()
        mtext = clipboard.wait_for_text()
        
        if ii == 0:
            if root[0].text != mtext:
                tclipb = None
                copy_iitem_text = root[0].text
                data = False
                root.remove(root[0])
                tree.write('history.xml')
                clipboard.clear()
                sleep(0.1)
                clipboard.set_text(copy_iitem_text, -1)
                self.on_row_clicked2()

            self.destroy()
        
        elif ii > 0:
            if list(root[ii].attrib.items())[0][1] == "Text":
                copy_iitem_text = root[ii].text
                data = False
                root.remove(root[ii])
                tree.write('history.xml')
                clipboard.set_text(copy_iitem_text, -1)
                self.on_row_clicked2()

            self.destroy()

    def on_copy_image(self, widget, cc):
        global data
        data = False
        cp = self.notebook.get_current_page()
        if cp == 1:
            copy_iitem_image = cc[-cp]
            tree = ET.parse('history.xml')
            root = tree.getroot()
            clipboard.clear()
            pixbuf0 = Pixbuf.new_from_file("images/"+copy_iitem_image)
            os.remove("images/"+copy_iitem_image)
            self.notebook.remove_page(cp)
            clipboard.set_image(pixbuf0)
        
        if cp > 1:
            copy_iitem_image = cc[-cp]
            tree = ET.parse('history.xml')
            root = tree.getroot()
            clipboard.clear()
            pixbuf0 = Pixbuf.new_from_file("images/"+copy_iitem_image)
            os.remove("images/"+copy_iitem_image)
            self.notebook.remove_page(cp)
            clipboard.set_image(pixbuf0)
        
        sleep(0.1)
        self.on_row_clicked2()
        self.destroy()
    
    def on_isavebutton_clicked(self, widget, cc):

        cp = self.notebook.get_current_page()
        copy_iitem_image = cc[-cp]
        copyfile("images/"+copy_iitem_image, str(Path.home())+"/"+copy_iitem_image)
    
    def on_tdelbutton_clicked(self, widget, listboxrow):

        ii = listboxrow.get_index()
        self.listbox.remove(self.listbox.get_row_at_index(ii))
        global data
        tree = ET.parse('history.xml')
        root = tree.getroot()
        rroot_len = root.__len__()
        
        if ii == 0:
            if rroot_len == 1:
                copy_iitem_text = root[0].text
                root.remove(root[0])
                tree.write('history.xml')
                #clipboard.clear()
                global tclipb
                tclipb = None
                sleep(0.1)
                self.destroy()
            
            elif rroot_len > 1:
                copy_iitem_text = root[ii+1].text
                data = False
                root.remove(root[ii+1])
                sleep(0.1)
                root.remove(root[ii])
                tree.write('history.xml')
                clipboard.set_text(copy_iitem_text, -1)
                self.on_row_clicked2()
                #self.destroy()

        elif ii > 0:
            copy_iitem_text = root[ii].text
            root.remove(root[ii])
            tree.write('history.xml')
            sleep(0.1)
            #self.destroy()
        
        iint = int(self.label1.get_text().replace("in history","").strip())
        self.label1.set_text("<b>{}</b> in history".format(str(iint-1)))
        self.label1.set_use_markup(True)

    def on_idelbutton_clicked(self, widget, cc):
        
        cp = self.notebook.get_current_page()
        tree = ET.parse('history.xml')
        root = tree.getroot()
        icp = int(self.label0.get_text().replace("image(s)","").strip())
        self.notebook.remove_page(cp)
        os.chdir(images_path)
        remove_iimage = cc[-cp]
        os.remove(remove_iimage)
        os.chdir(ccdir)
        del cc[-cp]
        #clipboard.clear()
        global ccrc2
        ccrc2 = 0
        self.label0.set_text("<b>{}</b> image(s)".format(icp-1))
        self.label0.set_use_markup(True)
        sleep(0.1)
        self.destroy()

    def on_preview_dialog(self, button, listboxrow, data = None):
        ii = listboxrow.get_index()
        tree = ET.parse('history.xml')
        root = tree.getroot()
        mtext = root[ii].text
        messagedialog1 = Gtk.MessageDialog(parent=self,
                                          modal=True,
                                          destroy_with_parent=True,
                                          message_type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK,
                                          text=None)
        
        messagedialog1.set_default_size(800, 450)
        messagedialog1.set_resizable(True)
        dialogbox = messagedialog1.get_content_area()
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        dialogbox.pack_end(scrolledwindow, True, True, 0)

        mlabel = Gtk.Label(label=mtext)
        mlabel.set_selectable(True)
        mlabel.set_line_wrap(True)
        scrolledwindow.add(mlabel)
        
        messagedialog1.connect("response", self.dialog_response1)
        messagedialog1.show_all()

    def dialog_response1(self, messagedialog1, response_id):
        if response_id == Gtk.ResponseType.OK:
            messagedialog1.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog1.destroy()

    def on_empty_clicked(self, button):
        messagedialog = Gtk.MessageDialog(parent=self,
                                          flags=Gtk.DialogFlags.MODAL,
                                          type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK_CANCEL,
                                          message_format="History will be empty. Continue?")
        messagedialog.connect("response", self.dialog_response)
        messagedialog.show()

    def dialog_response(self, messagedialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.on_empty1_clicked(messagedialog)
            messagedialog.destroy()
            self.destroy()
        elif response_id == Gtk.ResponseType.CANCEL:
            messagedialog.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog.destroy()

    def on_empty1_clicked(self, widget):
        global data
        clipboard.set_text("", -1)
        clipboard.clear()
        
        data = False
        try:
            os.unlink("history.xml")
        except Exception as e:
            pass
        
        with open("history.xml",'w') as fp:
            fp.write('<history version="1.0">'+'\n'+'</history>')
        
        for ffile in os.listdir(images_path):
            file_path = os.path.join(images_path, ffile)
            try:
                os.unlink(file_path)
            except Exception as e:
                pass
        global tclipb
        global ccrc2
        tclipb = None
        ccrc2 = 0
        self.on_row_clicked2()

## applet and daemon

tree = ET.parse('history.xml')
root = tree.getroot()

ftext = ""
text = ""   
pixbuf = None

class DaemonClip():

    def __init__(self):
        clipboard.connect('owner-change', self.clipb)
        
    def clipb(self, clipboard, EventOwnerChange):
        if SKIP_FILES:
            target_atoms = clipboard.get(Gdk.atom_intern("CLIPBOARD", True)).wait_for_targets()[1]
            targets = [item.name() for item in target_atoms ]
            if ("text/uri-list" not in targets) or ("x-special/gnome-copied-files" not in targets):
                clipboard.request_text(self.callback1, None)
                clipboard.request_image(self.callback2, None)
        else:
            clipboard.request_text(self.callback1, None)
            clipboard.request_image(self.callback2, None)
    
    def callback1(self, clipboard, text, data):
        if text:
            self.ccontent(text, None)
        
    def callback2(self, clipboard, pixbuf, data):
        if pixbuf:
            self.ccontent(None, pixbuf)

    def ccontent(self, ctdata, cidata):
        global tclipb
        global ftext
        global ccrc2
        global ccrc
        global ttext
        ttext = ""
        
        if data == True:
        # text
            ttext = ctdata
            iimage = cidata
            if ttext:
                if ttext != tclipb or ftext == "":
                    tree = ET.parse('history.xml')
                    root = tree.getroot()
                    child = ET.Element('item', kind="Text")
                    root.insert(0, child)
                    child.text = ttext
                    tree = ET.ElementTree(root)
                    tree.write('history.xml')
                    tclipb = ttext
                    ftext = ttext
        # image    
            elif iimage:
                ttime = time()
                ccrc = zlib.crc32(iimage.get_pixels())
                if ccrc != ccrc2:
                    try:
                       os.chdir(images_path)
                       iimage.savev(str(ttime)+".tiff", "tiff", [], [])
                    except AttributeError as err:
                        pass
                    finally:
                        os.chdir(ccdir)
                ccrc2 = ccrc
                
            else:
                ccrc2 = 0
                ccrc = 0
                ftext = ""
    
DaemonClip()

class StatusIcon:
    def __init__(self):
        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_from_file("gpasteboard.png")
        self.status_icon.connect("popup-menu", self.on_right_click)
        self.status_icon.connect('activate', self.on_left_click)
   
    def on_left_click(self, event):
        if data: 
            global main_window
            if main_window:
                win = MainWindow()
                main_window = False
        else:
            main_window = True
        
    def on_right_click(self, icon, button, time):
        self.menu = Gtk.Menu()
        termdaemon = Gtk.MenuItem()
        termdaemon.set_label("Stop/Start tracking")
        termdaemon.connect("activate", self.set_data)
        self.menu.append(termdaemon)
        
        eexit = Gtk.MenuItem()
        eexit.set_label("Exit")
        eexit.connect("activate", Gtk.main_quit)
        self.menu.append(eexit)
        self.menu.show_all()
        self.menu.popup(None, None, None, self.status_icon, button, time)

    def set_data(self, widget):
        global data
        if data:
            if main_window == True:
                data = False
                self.status_icon.set_from_file("gpasteboard-stop.png")
        else:
            self.status_icon.set_from_file("gpasteboard.png")
            data = True

def main():
    m = StatusIcon()
    Gtk.main()

if __name__ == '__main__':
    main()

