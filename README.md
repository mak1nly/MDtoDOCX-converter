# MDtoDOCX

[English](#english) · [Русский](#русский)

## Русский

Для запуска на Windows x64 откройте **MDtoDOCX.exe** двойным щелчком. Python, Qt и конвертер уже включены в файл. Приложение создаёт DOCX локально и работает без установленного Microsoft Word.

### Редактор

В обоих окнах предпросмотра выделите фрагмент и нажмите **Ctrl+C**. Без выделения **Ctrl+C** копирует весь текст предпросмотра. Эти команды доступны и по правому щелчку.

Выберите пресет и нажмите «Скопировать словарь». В буфер попадут параметры оформления и общие правила Markdown на языке интерфейса. Загрузите Markdown в UTF-8 или вставьте его слева, затем нажмите «Сохранить DOCX». Предпросмотр переключается между образцом и вашим текстом. Разбивку на страницы и номера страниц оглавления рассчитывает Word. Поле оглавления можно обновить через контекстное меню.

«Изменить» открывает настройки выбранного пресета, «+» создаёт новый. Справа от параметров расположен живой образец. Изменения применяются к пресету кнопкой «Сохранить». Настраиваются формат и ориентация листа, четыре поля, шрифт, размер, выравнивание, межстрочный интервал, отступ первой строки и интервалы абзацев. Для каждого из шести уровней заголовков доступны размер, начертание, выравнивание и интервалы. У таблиц можно включать границы и полужирную шапку.

Во вкладке «Настройки» доступны русский и английский языки, светлая, тёмная и системная темы. Пресеты и предпочтения сохраняются в preferences.json в пользовательской папке настроек MDtoDOCX. Редактируемый Markdown хранится в памяти до закрытия окна.

### Работа с исходным кодом

Этот раздел понадобится, если вы хотите изменить код, запустить тесты или собрать собственный EXE. Установите Python 3.12 x64 и откройте PowerShell в папке проекта.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Чтобы проверить изменения, выполните `python -m unittest discover -s tests -v`. Для сборки установите PyInstaller командой `python -m pip install pyinstaller==6.22.3`, затем выполните `.\build.ps1`. Готовый файл появится в `dist/MDtoDOCX.exe`.

`app.py` содержит главное окно. В `mdword/` находятся парсер Markdown, настройки пресетов, редактор шаблонов, предпросмотр, переводы и экспорт DOCX. Изображения для окна и исполняемого файла хранятся в `assets/`.

## English

On 64-bit Windows, double-click **MDtoDOCX.exe** to start. The executable includes Python, Qt and the converter. It creates DOCX files locally and works without Microsoft Word installed.

### Editor

In either preview, select a passage and press **Ctrl+C**. With no selection, **Ctrl+C** copies the entire preview text. You can also right-click to copy.

Choose a preset and select **Copy dictionary**. The clipboard will contain the formatting settings and shared Markdown rules in the interface language. Open a UTF-8 Markdown file or paste its contents into the left pane, then select **Save DOCX**. Switch the preview between the preset sample and your own document. Word calculates pagination and table of contents page numbers. To refresh the table of contents in Word, right-click it and choose **Update Field**.

Select **Edit** to change the current preset or **+** to create one. The sample to the right updates as you edit. Select **Save** to apply the changes. You can adjust paper size, orientation, all four margins, font, size, alignment, line spacing, first-line indent and paragraph spacing. Each of the six heading levels has its own size, weight, alignment and spacing. Tables support optional borders and a bold header row.

Under **Settings**, choose Russian or English and a light, dark or system theme. Presets and preferences are stored in `preferences.json` in the user's MDtoDOCX settings folder. Markdown in the editor stays in memory until the window closes.

### Working with the source code

Use this section to change the code, run the tests or build your own executable. Install 64-bit Python 3.12 and open PowerShell in the project directory.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

To test your changes, run `python -m unittest discover -s tests -v`. To build the executable, install PyInstaller with `python -m pip install pyinstaller==6.22.3`, then run `.\build.ps1`. The resulting file is `dist/MDtoDOCX.exe`.

`app.py` contains the main window. The `mdword/` directory contains the Markdown parser, preset settings, template editor, preview, translations and DOCX export. The window and executable icons are in `assets/`.
