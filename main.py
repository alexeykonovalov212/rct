def main():
    import pandas as pd
    import openpyxl
    import html
    import numpy as np
    import requests
    from bs4 import BeautifulSoup
    from selenium import webdriver
    import time

    second = 2
    #from requests.packages.urllib3.exceptions import InsecureRequestWarning

    #requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    url = 'https://torgi.gov.ru/new/api/public/lotcards/rss?subjRF=50&biddType=&biddForm=&currCode=&lotStatus=&biddEndFrom=&biddEndTo=&pubFrom=2022-12-15&pubTo=2022-12-15&aucStartFrom=&aucStartTo=&etpCode=&catCode=2&text=&noticeStatus=&amoOrgCode='
    req = requests.get(url, verify=False)
    soup = BeautifulSoup(req.text, features='lxml')

    num = soup.find_all('item')
    description_list = []
    for index in num:
        col = index.find(name='description')
        sel = html.unescape(col.text)
        description_list.append(sel)

    links_all = []
    for i in description_list:
        b = BeautifulSoup(i, features='lxml')
        link = b.find('a')
        link_final = link.get('href')
        links_all.append(link_final)

    driver = webdriver.Edge('C:\\Users\\KonovalovAlE\\Desktop\\jupyter notebook\\Вебдрайвер edge\\msedgedriver.exe')


    def data_parse(link):
        driver.get(link)
        time.sleep(second)
        main_page = driver.page_source
        soup = BeautifulSoup(main_page, features='xml')

        # Ищу местоположение
        place = np.NaN
        try:
            rent = soup.find_all(attrs={"class": {"lot-attr"}})
            for i in rent:
                if 'Местонахождение имущества' in i.text:
                    place = i.text.replace('Местонахождение имущества', '').strip()
        except:
            place = np.NaN

        # Площадь участка
        try:
            sq = soup.find_all(attrs={"class": {"lotAttributeDetail no-padding-bottom"}})
            square = sq[0].text.split('м')[0].strip()
        except:
            square = np.NaN

        # Описание лота
        try:
            head = soup.find_all(attrs={"class": {"header_title"}})
            header = head[0].text
        except:
            header = np.NaN

        # Срок аренды
        try:
            rent = soup.find_all(attrs={"class": {"attr_value"}})
            try:
                rent_time = rent[23].text.strip()
            except:
                rent_time = np.NaN
            if len(rent_time) == 0:
                try:
                    rent_time = rent[24].text.strip()
                except:
                    if len(rent_time) == 0:
                        rent_time = rent[17].text.strip() + ' месяца'
                        if rent_time == 'в соответствии с Извещением месяца':
                            rent_time = rent[16].text.strip() + ' месяца'
            if rent_time == 'Не разграниченная собственность':
                rent_time = ''
            if rent_time == 'Только для МСП':
                rent_time = rent[24].text.strip()
        except:
            rent_time = np.NaN

        # Начальная цена
        try:
            start = soup.find_all(attrs={"class": {"prices__row__price-cell lotPrice"}})
            start_price = start[0].text.split('₽')[0]
        except:
            start_price = np.NaN

        # Номер извещения

        num = soup.find_all(attrs={"class": {"lotAttributeValue"}})
        nums = num[0].text.split(',')
        number = nums[0].split('№')[1]


        # Номер лота

        lot = nums[1].split('№')
        lot_n = lot[0] + lot[1]
        lot_num = lot_n[1:]


        # Ссылка на лот, добавляю в итоговые данные по порядку

        # link которая передаётся в функцию

        # Дата окончания приема заявок
        try:
            date_cl = soup.find_all(attrs={"class": {"lotAttributeValue"}})
            date_close = date_cl[5].text[1:11]
        except:
            date_close = np.NaN

        # Дата торгов
        try:
            date_st = soup.find_all(attrs={"class": {"lotAttributeValue"}})
            date_start = date_st[6].text[1:11]
        except:
            date_start = np.NaN

        # Назначение
        try:
            Appointment = soup.find_all(attrs={"class": {"lotAttributeDetail no-padding-bottom"}})[-1].text.strip()
            if "50:" in Appointment:
                try:
                    Appointment = soup.find_all(attrs={"class": {"lotAttributeDetail no-padding-bottom"}})[
                        -2].text.strip()
                except:
                    Appointment = soup.find_all(attrs={"class": {"lotAttributeDetail no-padding-bottom"}})[
                        -3].text.strip()
        except:
            Appointment = np.NaN

        # Статус лота
        try:
            status = soup.find_all(attrs={"class": {"header_status prague"}})
            if len(list(status)) == 0:
                status = soup.find_all(attrs={"class": {"header_status amsterdam"}})[0].text.strip()
            else:
                status = soup.find_all(attrs={"class": {"header_status prague"}})[0].text.strip()
        except:
            status = np.NaN

        # Количество версий
        # Достаю ссылку на извещение

        linked = soup.find_all(attrs={"class": {"button text slim"}})

        link_to = 'https://torgi.gov.ru' + linked[0].get('href')

            # Загружаю ссылку через драйвер
        driver.get(link_to)
        time.sleep(second)
        main_page = driver.page_source
        soup = BeautifulSoup(main_page, features='xml')


        # Дата публикации
        try:
            lot = soup.find_all(attrs={"class": {"attr_value"}})

            dt_publ = lot[1].text[1:11]
        except:
            dt_publ = np.NaN

        # Организатор торгов

        auction_org = np.NaN
        try:
            for i in lot:
                if 'КОМИТЕТ' in i.text:
                    auction_org = i.text
                else:
                    auction_org = lot[7].text
        except:
            auction_org = np.NaN

        # Получаю количество версий
        try:
            versions = driver.find_element("class name", 'aside-btn')
            versions.click()
            time.sleep(second)
            action_time = driver.find_element("class name", "version-link").get_attribute('innerHTML').strip()
        except:
            action_time = np.NaN
        ###############################################

        try:
            list_of_data = [auction_org, place, square, header, rent_time, start_price, number, lot_num, link, dt_publ,
                            date_close, date_start, Appointment, status, action_time]
        except:
            list_of_data = np.NaN

        return list_of_data

    index = ['Организатор торгов', 'местоположение', 'Площадь ЗУ (кв.м)', 'Описание объекта', 'Срок передачи прав(лет)',
             'Начальнаяцена,загод', 'Номер извещения', 'Номер лота', 'Ссылка', 'Дата публикации',
             'Дата окончания приема заявок', 'Дата торгов/ подведения итогов/отмены', 'Назначение', 'Статус лота',
             'Количество версий']
    columns = list(range(0, len(links_all)))
    data = pd.DataFrame(index=index, columns=columns)

    for column in data.columns:
        data[column] = data_parse(links_all[column])

    data = data.T

    ####################################################################################################################

    col = ['#', 'Мониторинг на дату',
           'Блок',
           'Тип имущества', 'АТО', 'Организатор (сокр.)',
           'Наличие Соглашения',
           'Площадь помещения (кв.м.)', 'Срок передачи прав(месяц)', 'Срок передачи прав (дней)',
           'Начальная ежемесячная плата за объект, руб.', 'Дата отмены/ аннули-рования торгов']
    ind = [0, 1, 2, 4, 5, 6, 7, 10, 13, 14, 16, 23]

    for i in range(len(col)):
        data.insert(ind[i], col[i], np.NaN)

    data['#'] = 'АЕ'

    data['Мониторинг на дату'] = data['Дата публикации']

    for i in range(len(data['Организатор торгов'])):
        if data.loc[i,'Организатор торгов'] == 'КОМИТЕТ ПО КОНКУРЕНТНОЙ ПОЛИТИКЕ МОСКОВСКОЙ ОБЛАСТИ':
            data.loc[i,'АТО'] = 'Комитет/ГКУ РЦТ'
        else:
            data.loc[i,'АТО'] = np.NaN

    data['Тип имущества'] = 'ЗУ'

    ####################################################################################################################

    def izs_lpx(data):
        if data == 'Для индивидуального жилищного строительства':
            return 'ИЖС'
        elif data == 'Для ведения личного подсобного хозяйства (приусадебный земельный участок)':
            return 'ЛПХ'
        else:
            return data

    data['Назначение'] = data['Назначение'].apply(izs_lpx)

    data['Номер извещения'] = data['Номер извещения'].astype('str')

    data = data.sort_values(by='Количество версий').reset_index(drop=True)

    #data = data.dropna().reset_index(drop=True)


    file = 'C:\\Users\\KonovalovAlE\\Desktop\\База ЗУ (Парсинг)\\data_base.xlsx'  # указываем здесь путь к файлам
    wb = openpyxl.load_workbook(file)
    ws = wb.active

    from openpyxl.utils.dataframe import dataframe_to_rows
    rows = dataframe_to_rows(data, index=False)

    for r_idx, row in enumerate(rows, 1):
        for c_idx, value in enumerate(row, 1):
            ws.cell(row=r_idx, column=c_idx, value=value)

    wb.save(file)

if __name__ == "__main__":
    main()


