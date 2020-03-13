## Для инстала делаем
* git clone https://github.com/bratkovd/far_frr.git
* cd far_frr
* python -m venv venv
* venv\Scripts\activate
* pip install -r requirements.txt

## База данных и FRSDK
* Качаем http://vis-www.cs.umass.edu/lfw/lfw.tgz, распаковываем
* Качаем FRSDK, распаковываем, закидываем лицензию frsdk.lic в папку bin\Release_x64

## Подготавливаем задание для тестирования
* Открываем файл jobs.yml
* Пишем job1, 2, 3 и т.д. в формате YAML

### Параметры YAML
* type - range - диапазон прогонов по данной модели, single - один прогон
* model - тип модели A,B,C
* depth - в случае типом range указывается диапазон 1-100 или 3-30, где первое значение начало прогона, а второе конец. Если тип single, то указывается одно значение, например 90.
* count - количество лиц с http://vis-www.cs.umass.edu/lfw/devTest.html. если написали 100, то прогоним 100 из левого столбца и 100 из правого. максимальное значение 500
* step - если тип range, то указываем шаг смещения увеличения глубины.
* sdk_version - номер версии SDK для которого выполнить данную job. Например: '1.77.323'
* lfw_path - путь где лежит распакованная база данных с фотками LFW: http://vis-www.cs.umass.edu/lfw/lfw.tgz
* sdk_path - путь где лежат папки с распакованными SDK (1.70.300, 1.71.322 и т.д.)

## Для запуска распознавания выполняем
* python main.py

Готовые отчеты сваливаются в папку report, которая создается автоматически.

## Report

Результаты прогонов состоят из:
* Папка с датой и временем прогона
* Внутри csv файл *_match.csv в котором лежат результаты распознавания из левого столбца
* Внутри csv файл *_mismatch.csv в котором лежат результаты распознавания из правого столбца
* log.txt - лог хода выполнения теста, скорость работы, ERR, FAR, FRR
* *_line.png - графическое представление FAR и FRR к пороговому значениею

## Читалка логов
* python app.py
* Открываем браузер с ip:8000 и смотрим логи в веб интерфейсе
