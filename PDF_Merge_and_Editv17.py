import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
from PyPDF2.generic import create_string_object, DictionaryObject, NameObject
import os
import subprocess
import time
import sys
import webbrowser
import favicon
import tkinter as tk
from tkinter import filedialog
# Progressbar
import threading
import time
from tkinter import Button, Tk, HORIZONTAL, Listbox
from tkinter.ttk import Progressbar
# svg images
import tksvg
# ??? donno what is it
from functools import partial

#import dnd

# Written by Simon Wong
# https://github.com/simonwongwong

def recu(data):
    # Вообще должен читать закладки для листов,
    #но не все файлы и программы делают их, называя листы.
    #Здесь какой-то хаос, я пока сделал только для Арчикада.
    #print(f'RECU_{data}, {type(data)}')
    if  "/PieceInfo" in data.keys():
        if "/GRAPHISOFT" in data["/PieceInfo"]: # Защита от индезайн и ещё чего угодно
            #print('PI')
            return data["/PieceInfo"]["/GRAPHISOFT"]["/Private"]["/ACPageSource"]["/TargetName"]
    elif "/GRAPHISOFT" in data.keys():
        #print('GS')
        return data["/GRAPHISOFT"]["/Private"]["/ACPageSource"]["/TargetName"]
    elif  "/Private" in data.keys():
        #print('PR')
        return data["/Private"]["/ACPageSource"]["/TargetName"]
    elif  type(data) is not dict:
        for i in data:
            if type(i)  in (list, tuple) and len(i):
                print('LS')
                return recu(i)
            else:
                print('None of pagename')
                return "page"
    return None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def popup(text):
    textwindow = tk.Tk()
    textwindow.title('Оштбка!')
    textwindow.minsize(width=300, height=50)
    textwindow.resizable(False, False)
    label = tk.Label(textwindow, text=text)
    label.pack()
    label.configure(pady=20)
    textwindow.mainloop()

def finished(file, operation, window):
    stickyFill = tk.N + tk.E + tk.W + tk.S
    finishPrompt = tk.Tk()
    finishPrompt.title(operation + "Сделано!")
    finishPrompt.resizable(False, False)
    tk.Label(finishPrompt, text=operation + "Окончено. Открыть файл?").grid(row=0, column=0, columnspan=2, pady=5, padx=5)
    if 'win' not in os.sys.platform:
        tk.Button(finishPrompt, text="Открыть файл", command=lambda: subprocess.call(['evince',file])).grid(row=1, column=0, pady=5, padx=5, sticky=stickyFill)
    else:
        tk.Button(finishPrompt, text="Открыть файл", command=lambda: os.startfile(file)).grid(row=1, column=0, pady=5, padx=5, sticky=stickyFill)
    tk.Button(finishPrompt, text="Досвидулидам!", command=lambda: finishPrompt.destroy()).grid(row=1, column=1, pady=5, padx=5, sticky=stickyFill)
    finishPrompt.mainloop()

def filePicker(entry, window):
    file = filedialog.askopenfilename(title="Выбери PDF", filetypes=(("PDF", "*.pdf"),), initialdir=os.getcwd())

    if entry.get() == "":
        entry.insert(0, file)
    else:
        entry.delete(0, 'end')
        entry.insert(0, file)

    window.lift()

def folderPicker(entry, window):
    folder_path = filedialog.askdirectory()
    #print("Выбрана папка: ",folder_path)
    if entry.get() == "":
        entry.insert(0, folder_path)
    else:
        entry.delete(0, 'end')
        entry.insert(0, folder_path)
    window.lift()

def boomPages():
    stickyFill = tk.N + tk.E + tk.W + tk.S
    boomerWindow = tk.Tk()
    boomerWindow.title("Взорвать PDF на мелкие листы в папку.")
    boomerWindow.resizable(False, False)

    tk.Label(boomerWindow, text="Разделяет страницы PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(boomerWindow, text="PDF для редактирования:").grid(row=1, column=0, padx=10, pady=3)
    boomFile = tk.Entry(boomerWindow)
    boomFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(boomerWindow, text="Выбрать...", command=lambda entry=boomFile, window=boomerWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Button(boomerWindow, text="Разделить!", command=lambda: boomerWindow.quit()).grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    boomerWindow.mainloop()

    filename_ = boomFile.get()
    boomFile = checkExist(boomFile.get())
    originalPDF = PyPDF2.PdfReader(boomFile)
    directory, name_ = os.path.split(filename_)
    newdir = os.path.join(directory,'_separated')
    os.mkdir(newdir)
    if not boomFile:
        finished(filename_, "Разделение страницы", boomerWindow)
    for i in range(len(originalPDF.pages)):
        k = "%03d" % (i+1,)
        print(newdir,name_[:-4],k,'.pdf',end='\r')
        filename = os.path.join(newdir,f'{name_[:-4]}-sep-{str(k)}.pdf')
        outputFile = open(filename, 'wb')
        pdfOut = PyPDF2.PdfWriter()
        pdfOut.add_page(originalPDF.pages[i])
        pdfOut.write(outputFile)
        outputFile.close()

    boomerWindow.destroy()
    finished(filename_, "Разделение страницы", boomerWindow)

def mergePages():
    import tempfile

    class PDFManager:
        def __init__(self):
            self.pdf_files = {}  # {filename: (filepath, file_handle, PdfReader instance)}
            self.current_pdf = None

        def add_pdf(self, filepath):
            try:
                file_handle = open(filepath, 'rb')
                reader = PyPDF2.PdfReader(file_handle)
                self.pdf_files[filepath] = (filepath, file_handle, reader)
                return True
            except Exception as e:
                popup(f"Ошибка загрузки файла: {str(e)}")
                return False

        def get_pages(self, filepath):
            if filepath in self.pdf_files:
                return self.pdf_files[filepath][2].pages
            return []

        def set_current_pdf(self, filepath):
            if filepath in self.pdf_files:
                self.current_pdf = filepath

        def get_current_pages(self):
            if self.current_pdf:
                # Переоткрываем файл если он был закрыт
                filepath, file_handle, reader = self.pdf_files[self.current_pdf]
                if file_handle.closed:
                    file_handle = open(filepath, 'rb')
                    reader = PyPDF2.PdfReader(file_handle)
                    self.pdf_files[self.current_pdf] = (filepath, file_handle, reader)
                return reader.pages
            return []

        def close_all(self):
            for filepath, file_handle, _ in self.pdf_files.values():
                if not file_handle.closed:
                    file_handle.close()
            self.pdf_files.clear()

    def open_pdf_page(pdf_path, page_num):
        temp_pdf = PyPDF2.PdfWriter()
        pages = pdf_manager.get_pages(pdf_path)
        if page_num < len(pages):
            temp_pdf.add_page(pages[page_num])

        temp_path = os.path.join(tempfile.gettempdir(), f"temp_page_{page_num}.pdf")
        with open(temp_path, 'wb') as f:
            temp_pdf.write(f)

        if 'win' in os.sys.platform:
            os.startfile(temp_path)
        else:
            subprocess.call(['xdg-open', temp_path])

    def update_left_listbox():
        left_listbox.delete(0, tk.END)
        for filepath in pdf_manager.pdf_files:
            left_listbox.insert(tk.END, os.path.basename(filepath))

    def update_middle_listbox():
        middle_listbox.delete(0, tk.END)
        try:
            pages = pdf_manager.get_current_pages()
            for i in range(len(pages)):
                page = recu(pages[i]).replace(' ', '_').replace(':', '_').replace('\\', '_').replace('/', '_')
                middle_listbox.insert(tk.END, f"{page} {i + 1}")  # Формат: "аннотация номер_страницы"
        except Exception as e:
            popup(f"Ошибка загрузки страниц: {str(e)}")
            middle_listbox.delete(0, tk.END)


    def on_left_select(event):
        selection = left_listbox.curselection()
        if selection:
            filepath = list(pdf_manager.pdf_files.keys())[selection[0]]
            pdf_manager.set_current_pdf(filepath)
            update_middle_listbox()

    def move_to_right():
        selection = middle_listbox.curselection()
        if not selection or not pdf_manager.current_pdf:
            return

        for idx in selection:
            page_num = int(middle_listbox.get(idx).split()[1]) - 1
            page_name = middle_listbox.get(idx).split()[0]  # Получаем аннотацию
            right_listbox.insert(tk.END, (pdf_manager.current_pdf, page_num, page_name))  # Сохраняем аннотацию

    def remove_from_right():
        selection = right_listbox.curselection()
        for idx in reversed(selection):
            right_listbox.delete(idx)

    def move_up_right():
        selection = right_listbox.curselection()
        if not selection:
            return

        for pos in selection:
            if pos == 0:
                continue
            text = right_listbox.get(pos)
            right_listbox.delete(pos)
            right_listbox.insert(pos-1, text)
            right_listbox.selection_set(pos-1)

    def move_down_right():
        selection = right_listbox.curselection()
        if not selection:
            return

        for pos in reversed(selection):
            if pos == right_listbox.size()-1:
                continue
            text = right_listbox.get(pos)
            right_listbox.delete(pos)
            right_listbox.insert(pos+1, text)
            right_listbox.selection_set(pos+1)

    def merge_pdfs():
        if right_listbox.size() == 0:
            popup("Нет страниц для сшивания!")
            return

        output_file = filedialog.asksaveasfilename(
            title="Сохранить объединённый PDF",
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"),)
        )

        if not output_file:  # Если пользователь отменил сохранение
            return

        # Создаем окно прогресс-бара
        progress_window = tk.Toplevel(merge_window)
        progress_window.title("Сшивание PDF")
        progress_window.geometry("300x100")

        progress = Progressbar(progress_window, orient=tk.HORIZONTAL, length=280, mode='determinate')
        progress.pack(pady=20)

        label = tk.Label(progress_window, text="Идет процесс сшивания...")
        label.pack()

        def do_merge(output_file, progress, progress_window):
            try:
                writer = PdfWriter()
                total_pages = right_listbox.size()

                for i in range(total_pages):
                    pdf_path, page_num, page_name = right_listbox.get(i)

                    with open(pdf_path, 'rb') as file_handle:
                        reader = PdfReader(file_handle)
                        if page_num < len(reader.pages):
                            page = reader.pages[page_num]
                            new_page = writer.add_page(page)

                            # Добавляем аннотацию (как в предыдущих примерах)
                            target_name = create_string_object(str(page_name))
                            ac_page_source = DictionaryObject({NameObject("/TargetName"): target_name})
                            private_dict = DictionaryObject({NameObject("/ACPageSource"): ac_page_source})
                            graphisoft_dict = DictionaryObject({NameObject("/Private"): private_dict})

                            if NameObject("/PieceInfo") not in new_page:
                                new_page[NameObject("/PieceInfo")] = DictionaryObject()
                            new_page[NameObject("/PieceInfo")][NameObject("/GRAPHISOFT")] = graphisoft_dict

                    progress['value'] = (i + 1) / total_pages * 100
                    progress_window.update()

                # Сохраняем результат (без повторного запроса)
                with open(output_file, 'wb') as f:
                    writer.write(f)

                progress_window.destroy()
                finished(output_file, "Сшивание", merge_window)

            except Exception as e:
                progress_window.destroy()
                popup(f"Ошибка: {str(e)}")

        # Запускаем сшивание в отдельном потоке
        threading.Thread(target=do_merge, args=(output_file, progress, progress_window)).start()

    def add_pdfs():
        files = filedialog.askopenfilenames(
            title="Выберите PDF файлы",
            filetypes=(("PDF files", "*.pdf"),),
            initialdir=os.getcwd()
        )

        for file in files:
            if file not in pdf_manager.pdf_files:
                if pdf_manager.add_pdf(file):
                    update_left_listbox()

    def clear_all():
        pdf_manager.close_all()
        pdf_manager.current_pdf = None
        left_listbox.delete(0, tk.END)
        middle_listbox.delete(0, tk.END)
        right_listbox.delete(0, tk.END)

    # Initialize PDF manager
    pdf_manager = PDFManager()

    # Create main window
    merge_window = tk.Tk()
    merge_window.title("PDF сшить страницы")
    merge_window.geometry("1200x600")
    merge_window.minsize(800, 400)

    # Configure grid weights
    for i in range(3):
        merge_window.columnconfigure(i, weight=1, uniform="group1")
    merge_window.rowconfigure(1, weight=1)

    # Icons
    add_icon = "📄"
    open_icon = "👁"
    move_icon = "➡"
    remove_icon = "❌"
    merge_icon = "🔗"
    clear_icon = "🧹"
    up_icon = "⬆"
    down_icon = "⬇"


    # Left frame - PDF files list
    left_frame = tk.LabelFrame(merge_window, text="PDF файлы", padx=5, pady=5)
    left_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
    left_frame.columnconfigure(0, weight=1)
    left_frame.rowconfigure(0, weight=1)

    left_listbox = tk.Listbox(left_frame, selectmode=tk.EXTENDED) #selectmode=tk.SINGLE)
    left_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
    left_listbox.bind('<<ListboxSelect>>', on_left_select)

    left_buttons = tk.Frame(left_frame)
    left_buttons.grid(row=1, column=0, sticky=tk.EW, pady=5)

    tk.Button(left_buttons, text=add_icon + " Добавить", command=add_pdfs).pack(side=tk.LEFT, padx=2)
    tk.Button(left_buttons, text=clear_icon + " Очистить", command=clear_all).pack(side=tk.LEFT, padx=2)

    # Middle frame - Pages of selected PDF
    middle_frame = tk.LabelFrame(merge_window, text="Страницы выбранного PDF", padx=5, pady=5)
    middle_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)
    middle_frame.columnconfigure(0, weight=1)
    middle_frame.rowconfigure(0, weight=1)

    middle_listbox = tk.Listbox(middle_frame, selectmode=tk.EXTENDED)
    middle_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

    middle_buttons = tk.Frame(middle_frame)
    middle_buttons.grid(row=1, column=0, sticky=tk.EW, pady=5)

    tk.Button(middle_buttons, text=open_icon + " Просмотреть",
              command=lambda: (
                  open_pdf_page(
                      pdf_manager.current_pdf,
                      int(middle_listbox.get(middle_listbox.curselection()[0]).split()[1]) - 1
                  ) if pdf_manager.current_pdf and middle_listbox.curselection() else None
              )).pack(side=tk.LEFT, padx=2)

    # Right frame - Pages to merge
    right_frame = tk.LabelFrame(merge_window, text="Страницы для сшивания", padx=5, pady=5)
    right_frame.grid(row=1, column=2, sticky=tk.NSEW, padx=5, pady=5)
    right_frame.columnconfigure(0, weight=1)
    right_frame.rowconfigure(0, weight=1)

    right_listbox = tk.Listbox(right_frame, selectmode=tk.EXTENDED)
    right_listbox.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

    right_buttons = tk.Frame(right_frame)
    right_buttons.grid(row=1, column=0, sticky=tk.EW, pady=5)

    tk.Button(right_buttons, text=move_icon + " Добавить", command=move_to_right).pack(side=tk.LEFT, padx=2)
    tk.Button(right_buttons, text=remove_icon + " Удалить", command=remove_from_right).pack(side=tk.LEFT, padx=2)
    tk.Button(right_buttons, text=up_icon + " Вверх", command=move_up_right).pack(side=tk.LEFT, padx=2)
    tk.Button(right_buttons, text=down_icon + " Вниз", command=move_down_right).pack(side=tk.LEFT, padx=2)

    # Control buttons at the bottom
    control_frame = tk.Frame(merge_window)
    control_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)

    tk.Button(control_frame, text=merge_icon + " Сшить", command=merge_pdfs).pack(side=tk.RIGHT, padx=5)
    tk.Button(control_frame, text="Отмена", command=lambda: [pdf_manager.close_all(), merge_window.destroy()]).pack(side=tk.RIGHT, padx=5)

    merge_window.mainloop()

def mergePagesFolder():
    """
    Слияние из папки
    """
    stickyFill = tk.N + tk.E + tk.W + tk.S
    # Progressbar (as decorator?)
    def real_traitement(listbox, originalDir, mergeWindow, progress):
        progress.grid(row=1, column=0)
        progress.start()
        # process
        getval=listbox.get('active')
        mergedFile = path_+'.pdf' #mergedFile = mergedFile.get()
        mergedBook = PyPDF2.PdfMerger()
        for f in files_:
            mergedBook.append(f.name)
        fullbook = open(mergedFile + '.pdf', 'wb')
        mergedBook.write(fullbook)
        mergedBook.close()
        fullbook.close()
        progress.stop()
        progress.grid_forget()
        #btn['state']='normal'
        # Progressbar
        threading.Thread(target=real_traitement).start()
        finished(mergedFile + ".pdf", "Merge", mergeWindow)


    def get_pages(originalDir, window, listbox):
        folderPicker(originalDir, window)
        files_ = []
        listforbox = []
        for root, dirs, files in os.walk(originalDir.get()):
            path__ = root.split(os.sep)
            path_ = os.path.abspath(path__[-1])
            for file_ in files:
                #print(path__, file)
                if file_.endswith('pdf'):
                    #print("!! Имяфайла ",os.path.normpath(os.path.join(path_,file)))
                    files_.append(checkExist(os.path.normpath(os.path.join(path_,file_))))
                    listforbox.append(file_)
        for file_ in sorted(listforbox):
            listbox.insert("end", [file_])
        return files_


    def merge_items(listbox, originalDir, mergeWindow, progress):
        getval = [listbox.get(i) for i in listbox.curselection()]
        #print(getval)
        if not getval:
            getval = listbox.get(0,tk.END)
        odir = originalDir.get()
        path_ = os.path.abspath(odir)
        mergedFile = path_+'.pdf' #mergedFile = mergedFile.get()
        print("Ваш файл сохранён, как:",mergedFile)
        mergedBook = PyPDF2.PdfMerger()
        #print('files:',getval)
        for f in getval:
            #print('files: ',f[0])
            mergedBook.append(os.path.join(path_,f[0]))
        fullbook = open(mergedFile, 'wb')
        mergedBook.write(fullbook)
        mergedBook.close()
        fullbook.close()
        # mainloop traitment
        #btn['state']='disabled'
        mergeWindow.quit()
        mergeWindow.destroy()
        finished(mergedFile, "Merge", mergeWindow)

    def moveup(listbox, window):
        try:
            getval = listbox.get(0,tk.END)
            #print(getval)
            idxs = listbox.curselection()
            if not idxs:
                return
            for pos in idxs:
                if pos == 0:
                    continue
                text = listbox.get(pos)
                listbox.delete(pos)
                listbox.insert(pos-1, getval[pos])
                #self.animalList.pop(pos)
                #self.animalList.insert(pos-1, text)
                listbox.selection_set(pos-1)
        except:
            pass

    def movedown(listbox, window):
        try:
            getval = listbox.get(0,tk.END)
            #print(getval)
            idxs = listbox.curselection()
            if not idxs:
                return
            for pos in idxs:
                if pos == 0:
                    continue
                text = listbox.get(pos)
                listbox.delete(pos)
                listbox.insert(pos+1, getval[pos])
                #self.animalList.pop(pos)
                #self.animalList.insert(pos-1, text)
                listbox.selection_set(pos+1)
        except:
            pass

    mergeWindow = tk.Tk()
    mergeWindow.title("PDF сшить страницы")
    mergeWindow.resizable(True, True)
    mergeWindow.geometry('800x600+200+100')

    tk.Label(mergeWindow, text="Создаст новый PDF из выбранных файлов").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)
    #tk.Label(mergeWindow, text="Имя исходной папки:").grid(row=1, column=0)
    originalDir = tk.Entry(mergeWindow)
    originalDir.grid(row=1, column=1, padx=5, pady=5, sticky=stickyFill)

    progress = Progressbar(mergeWindow, orient=HORIZONTAL, length=100, mode='indeterminate')
    progress.grid(row=1, column=6, padx=5, pady=5, sticky=stickyFill)

    listbox=Listbox(mergeWindow, height=28, width=75, selectmode='extended',   font="arial 12") # selectmode='multiple',
    listbox.grid(row=1, rowspan=5, column=0, columnspan=5, padx=5, pady=5, sticky=stickyFill)
    #print("LISTBOX: ",listbox)
    # this button is used to invoke get_item function
    tk.Button(mergeWindow, text="Искать...", command=lambda listbox=listbox, entry=originalDir, window=mergeWindow: get_pages(entry, window, listbox)).grid(row=2, column=6, pady=5, padx=5, sticky=stickyFill)
    tk.Button(mergeWindow, text="Сшить!", command=lambda listbox=listbox, originalDir=originalDir, window=mergeWindow, progress=progress: merge_items(listbox, originalDir, window, progress)).grid(row=3, column=6, columnspan=3, padx=5, pady=10, sticky=stickyFill)
    tk.Button(mergeWindow, text="Вверх", command=lambda listbox=listbox, window=mergeWindow: moveup(listbox, window)).grid(row=4, column=6, columnspan=3, padx=5, pady=10, sticky=stickyFill)
    tk.Button(mergeWindow, text="Вниз", command=lambda listbox=listbox, window=mergeWindow: movedown(listbox, window)).grid(row=5, column=6, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    mergeWindow.mainloop()


def checkExist(fileName):
    try:
        openedFile = open(fileName, 'rb')
        print("Найден файл ",fileName)
        if fileName.endswith('pdf'):
            return openedFile
    except FileNotFoundError:
        popup(f'{fileName} не найден либо неисправен. Обратитесь к разработчику по ссылке «Описание проекта»')

def instructions():
    webbrowser.open("https://github.com/nortikin/PDF_Merge_and_Edit", new=2, autoraise=True)

# Обновленные кнопки в главном окне с иконками
def create_main_window():
    selector = tk.Tk()
    selector.configure(padx=10, pady=10)
    selector.title("PDF Редактор")
    icon = tk.PhotoImage(data=favicon.icon)
    selector.tk.call('wm', 'iconphoto', selector._w, icon)
    selector.resizable(False, False)

    stickyFill = tk.N + tk.E + tk.W + tk.S

    # Иконки для кнопок
    split_icon = "✂️"
    merge_icon = "📚"
    update_icon = "🔄"
    insert_icon = "⏏️"
    extract_icon = "📄"
    move_icon = "↔️"
    delete_icon = "❌"
    optimize_icon = "⚡"
    github_icon = "🐙"

    # body of GUI
    tk.Label(selector, text="Работа с PDF v 1.1.1").grid(row=1, column=1, pady=5, padx=5)

    tk.Button(selector, text=f"{split_icon} Разбить PDF файл в папку        ", command=boomPages).grid(row=2, column=0, columnspan=2, rowspan=2, sticky=stickyFill, pady=3, padx=5)
    tk.Button(selector, text=f"{merge_icon} Сшить PDF файл из файлов       ", command=mergePages).grid(row=4, column=0, columnspan=2, rowspan=2, sticky=stickyFill, pady=3, padx=5)
    tk.Button(selector, text=f"{insert_icon} Сшить PDF файл из папки       ", command=mergePagesFolder).grid(row=6, column=0, columnspan=2, rowspan=2, sticky=stickyFill, pady=3, padx=5)
    tk.Button(selector, text=f"{github_icon} Описание проекта в github       ", command=instructions).grid(row=8, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)

    selector.protocol("WM_DELETE_WINDOW", sys.exit)
    selector.mainloop()

# Замените вызов selector = tk.Tk() на:
if __name__ == "__main__":
    create_main_window()
