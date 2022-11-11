#!/usr/bin/env python3

# V. 1.9.1
############

from cfg import *

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, Pango
if STORE_IMAGES:
    from gi.repository.GdkPixbuf import Pixbuf
import os
import sys
from shutil import copyfile
from pathlib import Path
from time import time, sleep
import zlib

data = True

main_window = True

pint = 2
tclipb = None
ccrc = 0
ccrc2 = 0

ccdir = os.getcwd()
clips_path = os.path.join(ccdir, "clips")
images_path = os.path.join(ccdir, "images")

def cr_clips_images():
    if Path(clips_path).exists() == False:
        try:
            os.mkdir(clips_path)
        except:
            sys.exit()
    #
    if Path(images_path).exists() == False:
        try:
            os.mkdir(images_path)
        except:
            sys.exit()
cr_clips_images()

WINW = 400
WINH = 600

def cr_pd_size():
    if Path(os.path.join(ccdir, "progsize.cfg")).exists() == False:
        try:
            with open(os.path.join(ccdir, "progsize.cfg"), "w") as ffile:
                ffile.write("400;600")
        except:
            sys.exit()
    # #
    # if Path(os.path.join(ccdir, "dialogsize.cfg")).exists() == False:
        # try:
            # with open(os.path.join(ccdir, "dialogsize.cfg"), "w") as ffile:
                # ffile.write("400;400")
        # except:
            # sys.exit()
cr_pd_size()

try:
    ffile = open(os.path.join(ccdir, "progsize.cfg"), "r")
    WINW, WINH = ffile.readline().split(";")
    WINW = int(WINW)
    WINH = int(WINH)
    ffile.close()
except:
    WINW = 400
    WINH = 600

DWINW, DWINH = DIALOG_SIZE.split(";")
DWINW = int(DWINW)
DWINH = int(DWINH)
# try:
    # ffile = open(os.path.join(ccdir, "dialogsize.cfg"), "r")
    # DWINW, DWINH = ffile.readline().split(";")
    # DWINW = int(DWINW)
    # DWINH = int(DWINH)
    # ffile.close()
# except:
    # DWINW = 400
    # DWINH = 400

clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
clipboard.set_text("", -1)
clipboard.clear()

################# Program window

WW = WINW
HH = WINH
DWW = DWINW
DWH = DWINH

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Gpasteboard")
        self.connect("destroy", self.wclose)
        self.set_icon_from_file("clipman.svg")
        self.set_border_width(5)
        self.resize(WINW, WINH)
        #
        self.set_resizable(True)
        self.set_position(1)
        #
        self.hbox = Gtk.Box(spacing=10)
        self.hbox.set_homogeneous(False)
        self.add(self.hbox)
        #
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.hbox.pack_start(self.grid, False, False, 1)

        self.label1 = Gtk.Label(label="<b>0</b> in history")
        self.label1.set_use_markup(True)
        self.grid.attach(self.label1, 0, 0, 1, 1)
        self.grid.set_row_spacing(30)
        #
        if STORE_IMAGES:
            self.label2 = Gtk.Label(label="<b>0</b> image(s)")
            self.label2.set_use_markup(True)
            self.grid.attach(self.label2, 0, 1, 1, 1)
        #
        self.button1 = Gtk.Button(label="Empty history")
        self.button1.connect("clicked", self.on_empty_clicked)
        self.grid.attach(self.button1, 0, 2, 1, 1)
        #
        self.button2 = Gtk.Button(label="Quit")
        self.button2.connect("clicked", self.cclose)
        self.button2.props.valign = 2
        self.button2.props.vexpand = True
        self.grid.attach(self.button2, 0, 3, 1, 1)
        #
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.hbox.pack_start(self.notebook, True, True, 0)
        #
        self.page1 = Gtk.Box()
        self.page1.set_border_width(10)
        self.notebook.append_page(self.page1, Gtk.Label(label='Text'))
        #
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_placement(Gtk.CornerType.TOP_RIGHT)
        self.page1.add(self.scrolledwindow)     
        #
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.scrolledwindow.add(self.listbox)
        #
        q = 0   
        iq = 0   
        ### clips
        clips_temp = os.listdir(clips_path)
        #
        for iitem in sorted(clips_temp, reverse=True):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            row.add(hbox)
            label = Gtk.Label(xalign=XALIGN)
            label.set_single_line_mode(True)
            #
            iitem_text = ""
            tfile = open(os.path.join(clips_path, iitem), "r")
            iitem_text = tfile.readlines()[0]
            tfile.close()
            #
            if len(str(iitem_text)) > CHAR_PREVIEW:
                # label.set_text(str(iitem_text)[0:int(CHAR_PREVIEW)].replace("\n", " "+u'\u00AC'+" ")+" [...]")
                label.set_text(str(iitem_text)[0:int(CHAR_PREVIEW)]+" [...]")
            else:
                # label.set_text(str(iitem_text).replace("\n", " "+u'\u00AC'+" "))
                label.set_text(str(iitem_text))
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
            hbox.pack_start(label, True, True, 10)
            hbox.pack_start(button2, False, False, 0)
            hbox.pack_start(button, False, False, 0)
            row.iitem = iitem
            self.listbox.add(row)
            q += 1
        self.label1.set_text("<b>{}</b> in history".format(q))
        self.label1.set_use_markup(True)
        self.listbox.connect("row-activated", self.on_row_clicked)
        ### images
        if STORE_IMAGES:
            cc = []
            all_images = sorted(os.listdir(images_path), reverse=True)
            for iitem in all_images[:]:
                if os.path.splitext(iitem)[1] == '.tiff':
                    cc.append(iitem)
            for iitem in reversed(cc):
                grid0 = Gtk.Grid(hexpand=True, vexpand=True)
                grid0.set_column_homogeneous(True)
                hbox0 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
                button0 = Gtk.Button()
                button0.set_tooltip_text("Copy this image.")
                button0.connect("clicked", self.on_copy_image)
                iicon = Gio.ThemedIcon(name="dialog-ok")
                iimage = Gtk.Image.new_from_gicon(iicon, Gtk.IconSize.BUTTON)
                button0.add(iimage)
                pixbuf = Pixbuf.new_from_file(os.path.join(images_path, iitem))
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
                button.connect("clicked", self.on_idelbutton_clicked)
                button2 = Gtk.Button()
                iicon2 = Gio.ThemedIcon(name="stock_save")
                iimage2 = Gtk.Image.new_from_gicon(iicon2, Gtk.IconSize.BUTTON)
                button2.add(iimage2)
                button2.set_tooltip_text("Save this image.")
                button2.connect("clicked", self.on_isavebutton_clicked)
                hbox0.pack_start(button0, True, True, 0)
                hbox0.pack_start(button2, True, True, 0)
                hbox0.pack_start(button, True, True, 0)
                grid0.attach(image, 0, 1, 1, 1)
                grid0.attach_next_to(hbox0, image, Gtk.PositionType.BOTTOM, 1, 1)
                page = Gtk.Box()
                page.add(grid0)
                label = Gtk.Label(label="Image")
                self.notebook.insert_page(page, label, 1)
                page.iitem = iitem
                grid0.show()
                image.show()
                button2.show()
                page.show()
                iq += 1
                global pint
                pint += 1
            #
            self.label2.set_text("<b>{}</b> image(s)".format(iq))
            self.label2.set_use_markup(True)
        #
        self.connect("size-allocate", self.on_size_allocate)
        self.show_all()
        self.notebook.set_current_page(0)
    
    def on_size_allocate(self, widget, allocation):
        global WW
        global HH
        self.resize(allocation.width, allocation.height)
        if allocation.width != WINW or allocation.height != WINH:
            WW = allocation.width
            HH = allocation.height
    
    def set_window_size(self):
        global WINW
        global WINH
        if WW != WINW or HH != WINH:
            try:
                with open(os.path.join(ccdir, "progsize.cfg"), "w") as ffile:
                   ffile.write("{};{}".format(WW, HH))
                WINW = WW
                WINH = HH
            except:
                pass
        #
        # global DWINW
        # global DWINH
        # if DWW != DWINW or DWH != DWINH:
            # try:
                # with open(os.path.join(ccdir, "dialogsize.cfg"), "w") as ffile:
                   # ffile.write("{};{}".format(DWW, DWH))
                # DWINW = DWW
                # DWINH = DWH
            # except Exception as E:
                # pass
    
    def wclose(self, w):
        self.set_window_size()
        global main_window
        main_window = True
        self.destroy()
    
    def cclose(self, w):
        self.destroy()

    def on_row_clicked2(self, dat = None):
        global data
        sleep(0.1)
        data = True

    def on_row_clicked(self, listbox, listboxrow):
        ii = listboxrow.get_index()
        global data
        global tclipb
        #
        clip_file = listboxrow.iitem
        copy_iitem_text = ""
        try:
            tfile = open(os.path.join(clips_path, clip_file), "r")
            copy_iitem_text = tfile.readlines()[0]
            tfile.close()
        except:
            return
        #
        if ii == 0:
            mtext = clipboard.wait_for_text()
            if copy_iitem_text != mtext:
                data = False
                tclipb = None
                clipboard.clear()
                sleep(0.1)
                clipboard.set_text(copy_iitem_text, -1)
                self.on_row_clicked2()
        else:
            data = False
            new_clip_file = str(int(time()))
            try:
                os.remove(os.path.join(clips_path, clip_file))
            except:
                self.on_row_clicked2()
                self.destroy()
            #
            clipboard.clear()
            sleep(0.1)
            clipboard.set_text(copy_iitem_text, -1)
            self.on_row_clicked2()
        #
        self.destroy()
    
    def on_copy_image(self, widget):
        global data
        data = False
        curr_page = self.notebook.get_current_page()
        copy_iitem_image = self.notebook.get_nth_page(curr_page).iitem
        clipboard.clear()
        pixbuf0 = Pixbuf.new_from_file(os.path.join(images_path, copy_iitem_image))
        os.remove(os.path.join(images_path, copy_iitem_image))
        self.notebook.remove_page(curr_page)
        clipboard.set_image(pixbuf0)
        #
        sleep(0.1)
        self.on_row_clicked2()
        self.destroy()
    
    def on_isavebutton_clicked(self, widget):
        curr_page = self.notebook.get_current_page()
        copy_iitem_image = self.notebook.get_nth_page(curr_page).iitem
        copyfile(os.path.join(images_path, copy_iitem_image), os.path.join(str(Path.home()), copy_iitem_image))
    
    def on_tdelbutton_clicked(self, widget, listboxrow):
        ii = listboxrow.get_index()
        #
        clip_file = listboxrow.iitem
        copy_iitem_text = ""
        try:
            tfile = open(os.path.join(clips_path, clip_file), "r")
            copy_iitem_text = tfile.readlines()[0]
            tfile.close()
        except:
            return
        #
        global data
        list_len = 0
        while self.listbox.get_row_at_index(list_len):
            list_len += 1
        #
        try:
            os.remove(os.path.join(clips_path, clip_file))
        except:
            return
        #
        self.listbox.remove(self.listbox.get_row_at_index(ii))
        list_len -= 1
        #
        if list_len == 0:
            self.destroy()
        #
        self.label1.set_text("<b>{}</b> in history".format(str(list_len)))
        self.label1.set_use_markup(True)
        
    def on_idelbutton_clicked(self, widget):
        curr_page = self.notebook.get_current_page()
        copy_iitem_image = self.notebook.get_nth_page(curr_page).iitem
        try:
            os.remove(os.path.join(images_path, copy_iitem_image))
        except:
            pass
        self.notebook.remove_page(curr_page)
        #
        global ccrc2
        ccrc2 = 0
        self.label2.set_text("<b>{}</b> image(s)".format(self.notebook.get_n_pages()+1))
        self.label2.set_use_markup(True)
        sleep(0.1)
        self.destroy()

    def on_preview_dialog(self, button, listboxrow, data = None):
        clip_file = listboxrow.iitem
        copy_iitem_text = ""
        try:
            tfile = open(os.path.join(clips_path, clip_file), "r")
            copy_iitem_text = tfile.readlines()
            tfile.close()
        except:
            return
        #
        messagedialog1 = Gtk.MessageDialog(parent=self,
                                          modal=True,
                                          destroy_with_parent=True,
                                          message_type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK,
                                          text=None)
        #
        messagedialog1.set_default_size(DWW, DWH)
        messagedialog1.set_resizable(True)
        dialogbox = messagedialog1.get_content_area()
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        dialogbox.pack_end(scrolledwindow, True, True, 0)
        #
        copy_iitem_text2 = "".join(copy_iitem_text) 
        mlabel = Gtk.Label(label=copy_iitem_text2)
        mlabel.set_selectable(True)
        mlabel.set_line_wrap(True)
        scrolledwindow.add(mlabel)
        #
        # messagedialog1.connect("size-allocate", self.on_dialog_size_allocate)
        messagedialog1.connect("response", self.dialog_response1)
        messagedialog1.show_all()
    
    # def on_dialog_size_allocate(self, widget, allocation):
        # global DWW
        # global DWH
        # if allocation.width != DWINW or allocation.height != DWINH:
            # DWW = allocation.width
            # DWH = allocation.height
    
    def dialog_response1(self, messagedialog1, response_id):
        if response_id == Gtk.ResponseType.OK:
            messagedialog1.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog1.destroy()

    def on_empty_clicked(self, button):
        messagedialog = Gtk.MessageDialog(parent=self,
                                          modal=True,
                                          message_type=Gtk.MessageType.WARNING,
                                          buttons=Gtk.ButtonsType.OK_CANCEL,
                                          text="History will be empty. Continue?")
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
        data = False
        #
        clip_files = os.listdir(clips_path)
        image_files = os.listdir(images_path)
        try:
            for tt in clip_files:
                os.remove(os.path.join(clips_path, tt))
            for tt in image_files:
                os.remove(os.path.join(images_path, tt))
        except:
            pass
        #
        global tclipb
        global ccrc2
        tclipb = None
        ccrc2 = 0
        #
        self.on_row_clicked2()
        self.destroy()


## applet and daemon

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
            if len(text) < CLIP_MAX_SIZE:
                self.ccontent(text, None)
        
    def callback2(self, clipboard, pixbuf, data):
        if STORE_IMAGES and pixbuf:
            self.ccontent(None, pixbuf)

    def ccontent(self, ctdata, cidata):
        global tclipb
        global ftext
        global ccrc2
        global ccrc
        global ttext
        ttext = ""
        #
        if data == True:
            # text
            ttext = ctdata
            iimage = cidata
            if ttext:
                if ttext != tclipb or ftext == "":
                    time_now = str(int(time()))
                    i = 0
                    while os.path.exists(time_now):
                        time_now = str(int(time()))
                        i += 1
                        if i == 10:
                            break
                        return
                    #
                    try:
                        with open(os.path.join(clips_path, time_now), "w") as ffile:
                            ffile.write(ttext)
                    except:
                        pass
                    #
                    tclipb = ttext
                    ftext = ttext
                    # remove redundand clips
                    list_clips = sorted(os.listdir(clips_path), reverse=True)
                    num_clips = len(list_clips)
                    #
                    if num_clips > int(HISTORY_SIZE):
                        iitem = list_clips[-1]
                        try:
                            os.remove(os.path.join(clips_path, iitem))
                        except:
                            pass
            # image    
            elif iimage:
                ttime = int(time())
                image_name = str(ttime)+".tiff"
                #
                i = 0
                while os.path.exists(os.path.join(images_path, image_name)):
                    ttime = int(time())
                    image_name = str(ttime)+".tiff"
                    i += 1
                    if i == 10:
                        break
                    return
                #
                ccrc = zlib.crc32(iimage.get_pixels())
                if ccrc != ccrc2:
                    try:
                       iimage.savev(os.path.join(images_path, image_name), "tiff", [], [])
                    except AttributeError as err:
                        pass
                    ccrc2 = ccrc
                    # remove redundand images
                    list_images = sorted(os.listdir(images_path), reverse=True)
                    num_images = len(list_images)
                    #
                    if num_images > int(HISTORY_SIZE_IMAGES):
                        iitem = list_images[-1]
                        try:
                            os.remove(os.path.join(images_path, iitem))
                        except:
                            pass
            #
            else:
                ccrc2 = 0
                ccrc = 0
                ftext = ""
    
DaemonClip()


################### Tray icon
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


m = StatusIcon()
Gtk.main()
