import os, requests, subprocess, re, datetime, time, yaml
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool

class Job():
    model = None
    depth = None
    count = None
    data_set = None
    sdk_path = None
    sdk_version = None
    results_recognize = None
    date_start_job = None

    # Количество успешных распознаваний "Самих к себе"
    success_match_count = 0
    # Количесмтво успешных распознавания "Чужой к чужому"
    success_mismatch_count = 0

    lfw_path = None

    def __init__(self, model='A', depth='1', count='10', lfw_path='E:\\lfw\\lfw', sdk_path='E:\\Recognize', sdk_version='1.77.323'):
        self.model = model
        self.depth = depth
        self.count = count
        self.lfw_path = lfw_path
        self.sdk_path = sdk_path
        self.sdk_version = sdk_version

        # Создаем папку для отчетов
        self.date_start_job = self.create_report_dir()

        self.data_set = self.get_pairs_dev_test()

        # Запускаем выполнение работы
        self.run_job()

    def get_pairs_dev_test(self):
        '''
        Функция формирования набора данных для тестирования распознавания.
        Данные берутся с сайта LFW.
        Данные усекаются по переменной count
        :return: словарь с ключами match_pairs и mismatch_pairs внутри которых словари с объектами сравнения
        {'match_pairs': [['Abdullah_Gul--13', 'Abdullah_Gul--14'], ['Abdullah_Gul--13', 'Abdullah_Gul--16'] ...
        '''
        try:
            req = requests.get('http://vis-www.cs.umass.edu/lfw/pairsDevTest.txt')

            file = open(os.path.join('report', self.date_start_job, 'pairsDevTest.txt'), "w")
            file.write(req.text)
            file.close()

            log_text = f'Получены данные для теста с http://vis-www.cs.umass.edu/lfw/pairsDevTest.txt'
            self.logger(log_text)
        except:
            log_text = f'Не удалось получить данные для теста с сайта http://vis-www.cs.umass.edu/lfw/pairsDevTest.txt'
            self.logger(log_text)
            exit(1)

        rfile = open(os.path.join('report', self.date_start_job, 'pairsDevTest.txt'), "r").readlines()

        counter = 1
        match_list = []
        mismatch_list = []

        for l in rfile:
            if (counter > 1) and (counter <= 501):
                n = l.split()
                match_list.append([n[0] + '--' + n[1], n[0] + '--' + n[2]])
            elif (counter > 501) and (counter <= 1001):
                n = l.split()
                mismatch_list.append([n[0] + '--' + n[1], n[2] + '--' + n[3]])

            counter += 1

        os.remove(os.path.join('report', self.date_start_job, 'pairsDevTest.txt'))
        data_set = {'match_pairs': match_list[0:int(self.count)], 'mismatch_pairs': mismatch_list[0:int(self.count)]}

        return data_set

    def get_abspath_photo_in_person_name(self, person_name):
        '''
        Функция по переданному имени нормализует его до полного названия файла с абсолютным путем до него.
        :param person_name: Abdullah_Gul--13
        :return: "E:\lfw\lfw\Abdullah_Gul\Abdullah_Gul_0013.jpg"
        '''

        data = person_name.split('--')

        if int(data[-1]) < 10:
            number = '000' + data[-1] + '.jpg'
        elif (int(data[-1]) >= 10) and (int(data[-1]) < 100):
            number = '00' + data[-1] + '.jpg'
        else:
            number = '0' + data[-1] + '.jpg'

        filename = data[0] + '_' + number

        path = os.path.abspath(os.path.join(self.lfw_path, data[0], filename))

        return path

    def comparison_pair_photo(self, photo_1, photo_2):
        '''
        Функция сравнения двух фотографий между собой используя утилиту face_recognize из состава FRSDK
        :param photo_1: абсолютный путь до фото 1
        :param photo_2: абсолютный путь до фото 2
        :return: float процент на сколько лицо с фото 1 похоже на лицо с фото 2
        '''
        try:
            # Определяем пути ко всем составляющим SDK
            face_recognize_path = os.path.join(self.sdk_path, 'frsdk_' + self.sdk_version, 'bin', 'Release_x64',
                                               'face_recognize.exe')
            frsdk_path = os.path.join(self.sdk_path, 'frsdk_' + self.sdk_version, 'bin', 'Release_x64', 'frsdk.dat')

            res = subprocess.Popen([face_recognize_path,
                                    frsdk_path,
                                    '--model', self.model,
                                    '--depth', str(self.depth),
                                    '--hide',
                                    photo_1, photo_2],
                                   stdout=subprocess.PIPE, shell=True)

            (out, err) = res.communicate()

            tmp_file = open(os.path.join('report', self.date_start_job, 'report.txt'), 'w')
            tmp_file.write(out.decode('UTF-8'))
            tmp_file.close()

            # Парсим процент из файла отчета
            file = open(os.path.join('report', self.date_start_job, 'report.txt')).readlines()
            percent = None

            for line in file:
                if re.findall('0=', line):
                    if percent == None:
                        percent = float(str(line.split('=')[-1]).replace('\n', ''))

            if percent == None:
                percent = -1

            log_text = photo_1 + ' - ' + photo_2 + f': {percent}'
            self.logger(log_text)
            print(log_text)
            os.remove(os.path.join('report', self.date_start_job, 'report.txt'))
        except Exception as e:
            print(e)
            percent = -1

        return percent

    def run_job(self):
        '''
        Функция которая выполняет сравнение всех людей из переменной data_set
        :return:
        '''
        # Засекаем время начала работы сравнения лиц
        start_time = time.time()

        log_text = f'Начинаем сравнивать {self.count} похожих людей с параметрами: Model {self.model}, Depth {self.depth}'
        self.logger(log_text)
        print(log_text)

        current_match_count = 0
        for match in self.data_set['match_pairs']:
            # Из всего массива делаем столько сколько указано в переменной count
            if current_match_count < int(self.count):
                photo_1 = self.get_abspath_photo_in_person_name(match[0])
                photo_2 = self.get_abspath_photo_in_person_name(match[1])

                percent = self.comparison_pair_photo(photo_1, photo_2)

                if percent != -1:
                    self.success_match_count += 1

                match.append(percent)
                current_match_count += 1
            else:
                match.append(False)

        # Выполняем сравнение разных людей и в массив добавляем процент похожести
        log_text = f'Начинаем сравнивать {self.count} разных людей с параметрами: Model {self.model}, Depth {self.depth}'
        print(log_text)
        self.logger(log_text)

        current_mismatch_count = 0
        for mismatch in self.data_set['mismatch_pairs']:
            # Из всего массива делаем столько сколько указано в переменной MATCH_COUNT
            if current_mismatch_count < int(self.count):
                photo_1 = self.get_abspath_photo_in_person_name(mismatch[0])
                photo_2 = self.get_abspath_photo_in_person_name(mismatch[1])

                percent = self.comparison_pair_photo(photo_1, photo_2)

                if percent != -1:
                    self.success_mismatch_count += 1

                mismatch.append(percent)
                current_mismatch_count += 1
            else:
                mismatch.append(False)

        # Формируем DataFrame объект pandas для расчетов данных одинаковых людей
        person_one = [self.get_abspath_photo_in_person_name(n[0]) for n in self.data_set['match_pairs']]
        person_two = [self.get_abspath_photo_in_person_name(n[1]) for n in self.data_set['match_pairs']]
        percent = [n[-1] for n in self.data_set['match_pairs']]

        match_df = pd.DataFrame({
            'one_person': person_one,
            'two_person': person_two,
            'percent': percent
        })

        # Формируем DataFrame объект pandas для расчетов данных разных людей
        person_one = [self.get_abspath_photo_in_person_name(n[0]) for n in self.data_set['mismatch_pairs']]
        person_two = [self.get_abspath_photo_in_person_name(n[1]) for n in self.data_set['mismatch_pairs']]
        percent = [n[-1] for n in self.data_set['mismatch_pairs']]

        mismatch_df = pd.DataFrame({
            'one_person': person_one,
            'two_person': person_two,
            'percent': percent
        })

        results_recognize = {'match': match_df, 'mismatch': mismatch_df}
        self.results_recognize = results_recognize

        # Логируем количество найденных лиц
        log_text = f'Найдено лиц сравнения себя к себе {self.success_match_count} из {self.count}, ' \
                   f'и чужой к чужому {self.success_mismatch_count} из {self.count}'

        self.logger(log_text)

        # Делаем отчеты
        self.generate_report_data(results_recognize)

        # Фиксируем время завершения работы сравнения
        end_time = time.time()
        self.logger(f'Время сравнения {int(self.count)*2} лиц - {end_time - start_time} сек. Скорость одного сравнения {(end_time - start_time)/(int(self.count)*2)} сек.')

    def generate_report_data(self, data):
        '''
        Функция создает все отчетные данные по замеру, и размещает в папке report
        _match.csv - результаты сравнения лиц из левой колонки
        _mismatch.csv - результаты сравнения лиц из правой колонки
        _line.png - изображение графика сравнения FAR и FRR

        :param data: словарь с DataFrame объектами, где ключ match или mismatch в зависимости от того какие данные нужны
        '''
        try:
            # Подготавливаем шаблон имени файла для отчета где есть инфа о модели, глубине и количестве данных
            report_name = self.date_start_job + '_model_' + str(self.model).upper() + '_depth_' + str(self.depth) + '_count_' \
                          + str(int(self.count)*2) + '_sdk_' + str(self.sdk_version)

            # Из словаря получаем объекты DataFrame
            match = data['match']
            mismatch = data['mismatch']

            # Создаем csv файл с результатами замера из левой колонки lfw
            match.to_csv(os.path.join('report', self.date_start_job, report_name + '_match.csv'))

            # Создаем csv файл с результатами замера из правой колонки lfw
            mismatch.to_csv(os.path.join('report', self.date_start_job, report_name + '_mismatch.csv'))

            # Начинаем считать FAR и FRR
            # Создаем пустой словарь с данными FAR и FRR на определенном пороге
            far_frr_data = {'FRR': [], 'FAR': [], 'threshold': [], 'difference': []}
            for i in range(1, 100, 1):
                threshold = i / 100
                # Добавляем пороговое значение в объект FAR и FRR
                far_frr_data['threshold'].append(threshold)

                try:
                    # Считаем FRR и результат кладем в объект far и frr
                    FRR = 1 - (len(match.loc[match['percent'] >= threshold]) / int(self.success_match_count))
                    far_frr_data['FRR'].append(FRR)
                except Exception as e:
                    print(e)
                    FRR = 1.0
                    far_frr_data['FRR'].append(FRR)

                try:
                    # Считаем FAR и результат кладем в объект far и frr
                    FAR = len(mismatch.loc[mismatch['percent'] >= threshold]) / int(self.success_mismatch_count)
                    far_frr_data['FAR'].append(FAR)
                except Exception as e:
                    print(e)
                    FAR = 0.0
                    far_frr_data['FAR'].append(FAR)

                try:
                    # Считаем разницу между FAR и FRR и результат кладем в объект far и frr
                    difference = abs(FRR-FAR)
                    far_frr_data['difference'].append(difference)
                except Exception as e:
                    print(e)
                    difference = 1
                    far_frr_data['difference'].append(difference)

            # Данные из объекта far_frr_data превращаем в DataFrame объект pandas
            data_pd = pd.DataFrame({
                'threshold': far_frr_data['threshold'],
                'FRR': far_frr_data['FRR'],
                'FAR': far_frr_data['FAR']
            })

            # Тут рисуем график
            plt.style.use('ggplot')
            plt.rcParams['figure.figsize'] = (5, 5)

            data_pd.plot(x='threshold', y=['FAR', 'FRR'])
            plt.savefig(os.path.join('report', self.date_start_job, report_name + '_line.png'))

            # Лог пишем значения FAR и FRR по порогу с шагом 10
            for n in far_frr_data['threshold'][::10]:
                index = far_frr_data['threshold'].index(n)
                log_text = f'Для порога {str(n)} ' \
                           f'FAR: {str(far_frr_data["FAR"][index])}, ' \
                           f'FRR: {str(far_frr_data["FRR"][index])}'
                self.logger(log_text)

            # Вычисляем ERR из объекта far и frr путем нахождения индекса с самым маленьким значением difference
            index_min_difference = far_frr_data['difference'].index(min(far_frr_data['difference']))
            log_text = f'Threshold ERR: {far_frr_data["threshold"][index_min_difference]}, при котором FAR ' \
                       f'{far_frr_data["FAR"][index_min_difference]} и FRR {far_frr_data["FRR"][index_min_difference]}'
            self.logger(log_text)

        except Exception as e:
            log_text = f'Не смогли создать файл отчета: {e}'
            self.logger(log_text)
            print(log_text)

    def create_report_dir(self):
        '''
        Функция создает структуру папок для отчетов.
        В переменную date_start_job запсиывается имя для папки отчета
        :return:
        '''
        # Создаем папку с отчетами если нет такой
        try:
            os.mkdir('report')
        except:
            pass

        # Получаем дату и время как строку
        date = datetime.datetime.now().isoformat().split('.')[0]. \
            replace(':', '_').replace('-', '_').replace('T', '_')

        # Создаем папку для отчетных файлов
        os.mkdir(os.path.join('report', date))

        return date

    def logger(self, string):
        '''
        Функция логирования хода выполнения программы.
        Пишет строку в файл вида log.txt
        :param string: Произвольный текст
        '''

        with open(os.path.join('report', self.date_start_job, 'log.txt'), 'a+', encoding='utf-8') as f:
            f.write(str(datetime.datetime.now().isoformat()) + ': ' + string + '\r')
            f.close()

if __name__ == '__main__':
    #new_job = Job(model='B', depth='25', count='5')

    jobs = yaml.load(open('jobs.yml', 'r'), Loader=yaml.SafeLoader)
    for job in jobs:
        if jobs[job]['type'] == 'range':
            # Получаем диапазон начала и конца глубины в job
            range_depth = jobs[job]['depth'].split('-')

            for i in range(int(range_depth[0]), int(range_depth[-1]), int(jobs[job]['step'])):
                Job(model=jobs[job]['model'], depth=str(i), count=jobs[job]['count'])

        elif jobs[job]['type'] == 'single':
            Job(model=jobs[job]['model'], depth=jobs[job]['depth'], count=jobs[job]['count'])