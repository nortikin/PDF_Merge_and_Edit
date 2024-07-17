import PyPDF2
import os
import subprocess
import time
import sys
import webbrowser
import favicon
import tkinter as tk
from tkinter import filedialog
from functools import partial
import dnd

# Written by Simon Wong
# https://github.com/simonwongwong


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
    finishPrompt = tk.Tk()
    finishPrompt.title(operation + "Сделано!")
    finishPrompt.resizable(False, False)
    tk.Label(finishPrompt, text=operation + "Окончено. Открыть файл?").grid(row=0, column=0, columnspan=2, pady=5, padx=5)
    if 'win' not in os.sys.platform:
        tk.Button(finishPrompt, text="Открыть файл", command=lambda: subprocess.call(['evince',file])).grid(row=1, column=0, pady=5, padx=5, sticky=stickyFill)
    else:
        tk.Button(finishPrompt, text="Открыть файл", command=lambda: os.startfile(file)).grid(row=1, column=0, pady=5, padx=5, sticky=stickyFill)
    tk.Button(finishPrompt, text="До свидания", command=lambda: finishPrompt.destroy()).grid(row=1, column=1, pady=5, padx=5, sticky=stickyFill)
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
    print(folder_path)
    if entry.get() == "":
        entry.insert(0, folder_path)
    else:
        entry.delete(0, 'end')
        entry.insert(0, folder_path)

    window.lift()

def mergePages(): #entry, window):

    '''
    интеграция прогресс-шкалы
    import threading
    import time
    from tkinter import Button, Tk, HORIZONTAL
    from tkinter.ttk import Progressbar
    class MonApp(Tk):
        def __init__(self):
            super().__init__()
            self.btn = Button(self, text='Traitement', command=self.traitement)
            self.btn.grid(row=0, column=0)
            self.progress = Progressbar(self, orient=HORIZONTAL, length=100, mode='indeterminate')
        def traitement(self):
            def real_traitement():
                self.progress.grid(row=1,column=0)
                self.progress.start()
                time.sleep(5)
                self.progress.stop()
                self.progress.grid_forget()
                self.btn['state']='normal'
            self.btn['state']='disabled'
            threading.Thread(target=real_traitement).start()
    if __name__ == '__main__':
        app = MonApp()
        app.mainloop()
    '''


    mergeWindow = tk.Tk()
    mergeWindow.title("PDF сшить страницы")
    mergeWindow.resizable(False, False)

    tk.Label(mergeWindow, text="Создаст новый PDF из набора файлов").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    '''
    версия 4
    1. Выбираем папку, не файл
    2. добавляем после выбора в окно спаренные строки rowspan=2 для всех найденных файлов
    3. слева от каждого файла ставим две стрелочки, вверх и вниз, чтобы менять индексы отображения, при нажатии перерисовать окно с новым порядком
    4. если не помещается, больше 30 строк - делаем два столбца (четыре по три спаренных)
    5. кнопка удаления файла справа

    Выбрать папку       Выбрать
    л
            ФАЙЛ_1.pdf      Х
    v
    л
            ФАЙЛ_2.pdf      Х
    v
    Соединить все файлы!
    '''
    tk.Label(mergeWindow, text="Имя исходной папки:").grid(row=1, column=0)
    originalDir = tk.Entry(mergeWindow)
    originalDir.grid(row=1, column=1, padx=5, pady=5, sticky=stickyFill)
    tk.Button(mergeWindow, text="Искать...", command=lambda entry=originalDir, window=mergeWindow: folderPicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)


    tk.Button(mergeWindow, text="Сшить!", command=lambda: mergeWindow.quit()).grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    mergeWindow.mainloop()

    files_ = []
    for root, dirs, files in os.walk(originalDir.get()):
        path_ = root.split(os.sep)[0]
        for file in files:
            #print(path_, file)
            if file.endswith('pdf'):
                #print(file,'endswith pdf')
                files_.append(checkExist(os.path.normpath(os.path.join(path_,file))))
    #print(f'files are {files_}')

    mergedFile = path_+'.pdf' #mergedFile = mergedFile.get()
    mergedBook = PyPDF2.PdfMerger()
    for f in files_:
        mergedBook.append(f.name)


    fullbook = open(mergedFile + '.pdf', 'wb')
    mergedBook.write(fullbook)
    mergedBook.close()
    fullbook.close()
    mergeWindow.destroy()
    finished(mergedFile + ".pdf", "Merge", mergeWindow)


def updatePages():
    updaterWindow = tk.Tk()
    updaterWindow.title("PDF обновить страницу")
    updaterWindow.resizable(False, False)

    tk.Label(updaterWindow, text="Обновит одну страницу PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(updaterWindow, text="Выбери PDF:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(updaterWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(updaterWindow, text="Выбрать...", command=lambda entry=updateFile, window=updaterWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(updaterWindow, text="Страница для обновления:").grid(row=2, column=0, padx=10, pady=3)
    pageToUpdate = tk.Entry(updaterWindow)
    pageToUpdate.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(updaterWindow, text="Выбери PDF с новой страницей:").grid(row=3, column=0, padx=10, pady=3)
    updatedPage = tk.Entry(updaterWindow)
    updatedPage.grid(row=3, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(updaterWindow, text="Выбрать...", command=lambda entry=updatedPage, window=updaterWindow: filePicker(entry, window)).grid(row=3, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(updaterWindow, text="Номер страницы:").grid(row=4, column=0, padx=10, pady=3)
    pageWithUpdate = tk.Entry(updaterWindow)
    pageWithUpdate.grid(row=4, column=1, sticky=stickyFill, pady=5, padx=5)
    pageWithUpdate.insert(0, "1")

    tk.Button(updaterWindow, text="Обновить!", command=lambda: updaterWindow.quit()).grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    updaterWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageToUpdate = int(pageToUpdate.get())
    filename = filename[:-4] + '-upd'+str(pageToUpdate)+'.pdf'
    updatedPage = checkExist(updatedPage.get())
    pageWithUpdate = int(pageWithUpdate.get())

    if pageToUpdate == 0 or pageWithUpdate == 0:
        popup("Число не верно, должно быть больше 0")

    originalPDF = PyPDF2.PdfReader(updateFile)
    updatedPagePDF = PyPDF2.PdfReader(updatedPage)

    updatedPDF = PyPDF2.PdfWriter()
    updatedPDF.clone_document_from_reader(originalPDF)
    try:
        updatedPDF.insert_page(updatedPagePDF.pages[pageWithUpdate - 1], pageToUpdate - 1)
    except IndexError:
        popup("Проверьте, входит ли номер страницы в диапазон листов")

    outputFile = open(filename, 'wb')

    pdfOut = PyPDF2.PdfWriter()

    for i in range(len(updatedPDF.pages)):
        if i != pageToUpdate:
            pdfOut.add_page(updatedPDF.pages[i])

    pdfOut.write(outputFile)
    outputFile.close()

    updaterWindow.destroy()
    finished(filename, "Обновление страницы", updaterWindow)



def movePages():
    moveWindow = tk.Tk()
    moveWindow.title("PDF переместить страницу")
    moveWindow.resizable(False, False)

    tk.Label(moveWindow, text="Переместить страницу PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(moveWindow, text="Начальный PDF:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(moveWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(moveWindow, text="Выбрать...", command=lambda entry=updateFile, window=moveWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(moveWindow, text="Номер страницы для перемещения:").grid(row=2, column=0, padx=10, pady=3)
    pageBefore = tk.Entry(moveWindow)
    pageBefore.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(moveWindow, text="Номер страницы, перед которым вставить:").grid(row=4, column=0, padx=10, pady=3)
    pageAfter = tk.Entry(moveWindow)
    pageAfter.grid(row=4, column=1, sticky=stickyFill, pady=5, padx=5)
    pageAfter.insert(0, "1")

    tk.Button(moveWindow, text="Переместить!", command=lambda: moveWindow.quit()).grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    moveWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageBefore = int(pageBefore.get())
    filename = filename[:-4] + '-mov-'+str(pageBefore)+'.pdf'
    pageAfter = int(pageAfter.get())

    if pageBefore == 0 or pageAfter == 0:
        popup("Число не верно, должно быть больше 0")

    originalPDF = PyPDF2.PdfReader(updateFile)
    updatedPDF = PyPDF2.PdfWriter()
    try:
        page_was_deleted = False
        for i in range(len(originalPDF.pages)):
            #updatedPDF.insert_page(originalPDF.pages[pageBefore - 1], pageAfter - 1)
            if i == pageBefore-1:
                # 1 - удаление страницы
                page_was_deleted = True
                continue
            elif i == pageAfter-1 and page_was_deleted:
                # 2 - добавление страницы после удалённой
                page_was_deleted = False
                updatedPDF.add_page(originalPDF.pages[i])
                updatedPDF.add_page(originalPDF.pages[pageBefore-1])
            elif i == pageAfter-1:
                # 3 - добавление страницы до удаления либо отработан 2
                updatedPDF.add_page(originalPDF.pages[pageBefore-1])
                updatedPDF.add_page(originalPDF.pages[i])
            else:
                # ряовое включение страницы
                updatedPDF.add_page(originalPDF.pages[i])

    except IndexError:
        popup("Проверьте, входит ли номер страницы в диапазон листов")

    #pdfOut = PyPDF2.PdfWriter()
    outputFile = open(filename, 'wb')
    updatedPDF.write(outputFile)
    outputFile.close()

    moveWindow.destroy()
    finished(filename, "Перемещение страницы", moveWindow)

def insertPages():
    inserterWindow = tk.Tk()
    inserterWindow.title("PDF вставить страницу")
    inserterWindow.resizable(False, False)

    tk.Label(inserterWindow, text="Вставить страницу внутрь PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(inserterWindow, text="Начальный PDF:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(inserterWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(inserterWindow, text="Выбрать...", command=lambda entry=updateFile, window=inserterWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(inserterWindow, text="Номер будущей страницы:").grid(row=2, column=0, padx=10, pady=3)
    pageToInsert = tk.Entry(inserterWindow)
    pageToInsert.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(inserterWindow, text="PDF с новой страницей:").grid(row=3, column=0, padx=10, pady=3)
    fileWithInsert = tk.Entry(inserterWindow)
    fileWithInsert.grid(row=3, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(inserterWindow, text="Выбрать...", command=lambda entry=fileWithInsert, window=inserterWindow: filePicker(entry, window)).grid(row=3, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(inserterWindow, text="Номер заимствованной страницы для вставки:").grid(row=4, column=0, padx=10, pady=3)
    pageWithInsert = tk.Entry(inserterWindow)
    pageWithInsert.grid(row=4, column=1, sticky=stickyFill, pady=5, padx=5)
    pageWithInsert.insert(0, "1")

    tk.Button(inserterWindow, text="Вставить!", command=lambda: inserterWindow.quit()).grid(row=5, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    inserterWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageToInsert = int(pageToInsert.get())
    filename = filename[:-4] + '-ins-'+str(pageToInsert)+'.pdf'
    fileWithInsert = checkExist(fileWithInsert.get())
    pageWithInsert = int(pageWithInsert.get())

    if pageToInsert == 0 or pageWithInsert == 0:
        popup("Число не верно, должно быть больше 0")

    originalPDF = PyPDF2.PdfReader(updateFile)
    PDFwithInsert = PyPDF2.PdfReader(fileWithInsert)

    updatedPDF = PyPDF2.PdfWriter()
    updatedPDF.clone_document_from_reader(originalPDF)
    try:
        updatedPDF.insert_page(PDFwithInsert.pages[pageWithInsert - 1], pageToInsert - 1)
    except IndexError:
        popup("Проверьте, входит ли номер страницы в диапазон листов")

    outputFile = open(filename, 'wb')

    pdfOut = PyPDF2.PdfWriter()

    for i in range(len(updatedPDF.pages)):
        pdfOut.add_page(updatedPDF.pages[i])

    pdfOut.write(outputFile)
    outputFile.close()
    inserterWindow.destroy()
    finished(filename, "Вставка страницы", inserterWindow)


def deletePages():
    deleterWindow = tk.Tk()
    deleterWindow.title("Удалить страницы из PDF")
    deleterWindow.resizable(False, False)
    '''
    вариант 4
    вместо диапазона парсить re строку типа 1,3,5-15, 23
    интерпретировать в 1,3,5,6,7,8,9,10,11,12,13,14,15,23
    автосортировка после распознавания, set() для исключения повторов
    пройтись с конца 23...1 для удаления листов
    имя включает начальную строку пользователя без пробелов
    '''

    tk.Label(deleterWindow, text="Удаляет диапазон страниц из PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(deleterWindow, text="PDF для редактирования:").grid(row=1, column=0, padx=10, pady=3)
    updateFile = tk.Entry(deleterWindow)
    updateFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(deleterWindow, text="Выбрать...", command=lambda entry=updateFile, window=deleterWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Label(deleterWindow, text="Первая страница:").grid(row=2, column=0, padx=10, pady=3)
    pageFromDelete = tk.Entry(deleterWindow)
    pageFromDelete.grid(row=2, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Label(deleterWindow, text="Последняя страница:").grid(row=3, column=0, padx=10, pady=3)
    pageToDelete = tk.Entry(deleterWindow)
    pageToDelete.grid(row=3, column=1, sticky=stickyFill, pady=5, padx=5)

    tk.Button(deleterWindow, text="Удалить!", command=lambda: deleterWindow.quit()).grid(row=4, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    deleterWindow.mainloop()

    filename = updateFile.get()
    updateFile = checkExist(updateFile.get())
    pageToDelete = int(pageToDelete.get())
    pageFromDelete = int(pageFromDelete.get())
    filename = f'{filename[:-4]}-del-{pageFromDelete}-{pageToDelete}.pdf'

    if pageToDelete == 0 or pageToDelete < pageFromDelete:
        popup("Число не верно, должно быть больше 0 и не в обратном порядке")

    originalPDF = PyPDF2.PdfReader(updateFile)

    updatedPDF = PyPDF2.PdfWriter()
    updatedPDF.clone_document_from_reader(originalPDF)
    try:
        for i in range(pageToDelete,pageFromDelete-1,-1):
            updatedPDF.pages[i - 1]
    except IndexError:
        popup("Проверьте, входит ли номер страницы в диапазон листов")

    outputFile = open(filename, 'wb')

    pdfOut = PyPDF2.PdfWriter()

    for i in range(len(updatedPDF.pages)):
        if i > pageToDelete - 1 or i < pageFromDelete - 1:
            pdfOut.add_page(updatedPDF.pages[i])

    pdfOut.write(outputFile)
    outputFile.close()

    deleterWindow.destroy()
    finished(filename, "Удаление страницы", deleterWindow)

def optimizePDF():
    optimizerWindow = tk.Tk()
    optimizerWindow.title("Оптимизировать PDF, уменьшить объём.")
    optimizerWindow.resizable(False, False)

    tk.Label(optimizerWindow, text="Оптимизирует PDF").grid(row=0, column=0, columnspan=3, padx=10, pady=3, sticky=stickyFill)

    tk.Label(optimizerWindow, text="Исходный PDF:").grid(row=1, column=0, padx=10, pady=3)
    optimizerFile = tk.Entry(optimizerWindow)
    optimizerFile.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
    tk.Button(optimizerWindow, text="Выбрать...", command=lambda entry=optimizerFile, window=optimizerWindow: filePicker(entry, window)).grid(row=1, column=2, pady=5, padx=5, sticky=stickyFill)

    tk.Button(optimizerWindow, text="Оптимизировать!", command=lambda: optimizerWindow.quit()).grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky=stickyFill)

    optimizerWindow.mainloop()

    filename_ = optimizerFile.get()
    filename = f'{filename_[:-4]}-opt.pdf'
    optimizerFile = checkExist(optimizerFile.get())
    originalPDF = PyPDF2.PdfReader(optimizerFile)
    outputFile = open(filename, 'wb')
    pdfOut = PyPDF2.PdfWriter()

    for page in originalPDF.pages:
        page.compress_content_streams()  # This is CPU intensive!
        pdfOut.add_page(page)
    pdfOut.write(outputFile)
    outputFile.close()
    optimizerWindow.destroy()
    finished(filename, "Оптимизатор PDF ", optimizerWindow)

def checkExist(fileName):
    try:
        openedFile = open(fileName, 'rb')
        if fileName.endswith('pdf'):
            return openedFile
    except FileNotFoundError:
        popup(f'{fileName} не найден либо неисправен. Обратитесь к разработчику по ссылке «Описание проекта»')

def boomPages():
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

def instructions():
    webbrowser.open("https://github.com/nortikin/PDF_Merge_and_Edit", new=2, autoraise=True)


selector = tk.Tk()
selector.configure(padx=10, pady=10)
selector.title("PDF Редактор")
icon = tk.PhotoImage(data=favicon.icon)
selector.tk.call('wm', 'iconphoto', selector._w, icon)
selector.resizable(False, False)

stickyFill = tk.N + tk.E + tk.W + tk.S

# body of GUI
tk.Label(selector, text="Работа с PDF:").grid(row=0, column=0, pady=5, padx=5)
tk.Label(selector, text="v 0.5.0").grid(row=0, column=1, pady=5, padx=5)
#nfiles = tk.IntVar()
#entry_ = tk.Entry(selector, text=nfiles)
#entry_.grid(row=1, column=1, sticky=stickyFill, pady=5, padx=5)
#nfiles.set(2)
#tk.Button(selector, text="Сшить PDFs", command=lambda entry=entry_, window=selector: merge(entry, window)).grid(row=1, column=1, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Разбить PDF файл в папку", command=boomPages).grid(row=1, columnspan=2, column=0, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Сшить PDF файл из папки", command=mergePages).grid(row=2, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Обновить страницу в PDF", command=updatePages).grid(row=3, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Втиснуть страницу в PDF", command=insertPages, padx=20).grid(row=4, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Переместить страницу PDF", command=movePages).grid(row=5, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Удалить страницы в PDF", command=deletePages).grid(row=6, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Оптимизировать PDF файл", command=optimizePDF).grid(row=7, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)
tk.Button(selector, text="Описание проекта в github", command=instructions).grid(row=8, column=0, columnspan=2, sticky=stickyFill, pady=3, padx=5)



selector.protocol("WM_DELETE_WINDOW", sys.exit)
selector.mainloop()
