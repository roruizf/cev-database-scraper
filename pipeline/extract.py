import requests
import lxml.html as html
import os
import datetime
from time import time
import json
import numpy as np
import pandas as pd
import math

HOME_URL = 'http://calificacionenergeticaweb.minvu.cl/Publico/BusquedaVivienda.aspx'


def flatten_list(_2d_list):
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if type(element) is list:
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


def form_data(eventtarget, eventargument, region, comuna, certification):
    with open('../json_files/viewstate.json') as json_file:
        viewstate_dict = json.load(json_file)
    viewstate = viewstate_dict[region]
    return {
        'ToolkitScriptManager2_HiddenField': ';;AjaxControlToolkit, Version=4.1.60501.0, Culture=neutral, PublicKeyToken=28f01b0e84b6d53e:es-CL:5c09f731-4796-4c62-944b-da90522e2541:de1feab2:f2c8e708:720a52bf:f9cec9bc:589eaa30:a67c2700:ab09e3fe:87104b7c:8613aea7:3202a5a2:be6fb298',
        '__EVENTTARGET': eventtarget,
        '__EVENTARGUMENT': eventargument,
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': '2B422A52',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '0',
        '__VIEWSTATEENCRYPTED': '',
        'ctl00$ContentPlaceHolder1$look': '0',
        'ctl00$ContentPlaceHolder1$dbRegion': region,
        'ctl00$ContentPlaceHolder1$dbComuna': comuna,
        'ctl00$ContentPlaceHolder1$dbCertificacion': certification,
        'ctl00$ContentPlaceHolder1$dbTipologia': '-1',
        'ctl00$ContentPlaceHolder1$TxtNombrePry': '',
        'ctl00$ContentPlaceHolder1$txtIdentificacion': '',
        'ctl00$ContentPlaceHolder1$txtCampo': '0',
        'ctl00$ContentPlaceHolder1$txtOrden': '0'
    }


def get_single_page_response(eventtarget, eventargument, region, comuna, certification):
    # eventtarget = 'ctl00$ContentPlaceHolder1$grdViviendasPre'
    # eventargument = 'Page$1'
    # region = '9'
    # comuna = '315'
    # certification = '1'     # Precalification: 1 / Calificacion: 2 / Both: '-1'
    formdata = form_data(eventtarget, eventargument,
                         region, comuna, certification)
    # 10 region
    # formdata['__VIEWSTATE'] = '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'
    # 9 region
    # formdata['__VIEWSTATE'] = '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'

    # Downloading data for a given day -> making sure the data is downladed (status_code == 200)
    status = True
    try_number = 1
    sleep_time = 1  # s
    while status:
        response = requests.post(HOME_URL, data=formdata)
        if response.status_code != 200:
            if try_number <= 10:
                print(
                    f"Status code is {response.status_code} at try number {try_number}, entering sleep for {sleep_time} second(s)")
                try_number += 1
                time.sleep(sleep_time)
            else:
                print(
                    f"Oops!  Maximum number of tries was reached ({try_number}).  Run the code again...")
                break
        else:
            status = False
    return response


def single_page_precalificacion(response):
    home = response.content.decode('utf-8')
    parsed = html.fromstring(home)
    # ---------------------------
    # Viviendas Pre-calificadas
    # ---------------------------
    # Messages for found (or not found) dwellings
    message_found_pre = parsed.xpath(
        '//strong/span[@id="ContentPlaceHolder1_ResultadoGrillaPre"]/descendant-or-self::*/text()')
    message_not_found_pre = parsed.xpath(
        '//span[@id="ContentPlaceHolder1_grdViviendasPre_Label21"]/text()')

    # Getting data for dwellings
    table_columns_pre = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasPre"]/thead/tr[@class="barra_superior"][1]/th[not(@class) and @scope="col"]/text()')
    vivienda_Id_pre = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[not(@class) and not(@style)][1]/text()')
    tipologia_pre = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[not(@class) and not(@style)][2]/text()')
    comuna_proyecto_pre = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[not(@class) and not(@style)][3]/text()')
    proyecto_pre = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[not(@class) and not(@style)][4]/text()')
    ce_pre_src = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[position() = (last()-2)]/div/img/@src')
    cee_pre_src = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasPre"]/tbody/tr/td[position() = (last()-1)]/div/img/@src')

    # Get the calification letter from src string
    ce_pre = [x.split('Letra')[1].split('.png')[0] for x in ce_pre_src]
    cee_pre = [x.split('Letra')[1].split('.png')[0] for x in cee_pre_src]

    # Creating a dictionary in order to create a dataframe
    if message_found_pre:
        # print(
        #     f'{message_found_pre[0]} {message_found_pre[1]} {message_found_pre[-1]}')
        vivienda_pre_dict = dict(zip(table_columns_pre, [
                                 vivienda_Id_pre, tipologia_pre, comuna_proyecto_pre, proyecto_pre, ce_pre, cee_pre]))
    else:
        # print(f'{message_not_found_pre[0]}')
        vivienda_pre_dict = dict(
            zip(table_columns_pre, [[], [], [], [], [], []]))
    viviendas_pre_df = pd.DataFrame.from_dict(data=vivienda_pre_dict)
    return viviendas_pre_df


def single_page_calificacion(response):
    home = response.content.decode('utf-8')
    parsed = html.fromstring(home)
    # ---------------------------
    # Viviendas Calificadas
    # ---------------------------
    # Messages for found (or not found) dwellings
    message_found_cal = parsed.xpath(
        '//strong/span[@id="ContentPlaceHolder1_ResultadoGrillaCal"]/descendant-or-self::*/text()')
    message_not_found_cal = parsed.xpath(
        '//span[@id="ContentPlaceHolder1_grdViviendasCal_Label21"]/text()')

    # Getting data for dwellings
    table_columns_cal = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasCal"]/thead/tr[@class="barra_superior"][1]/th[not(@class) and @scope="col"]/text()')
    vivienda_Id_cal = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[not(@class) and not(@style)][1]/text()')
    tipologia_cal = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[not(@class) and not(@style)][2]/text()')
    comuna_proyecto_cal = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[not(@class) and not(@style)][3]/text()')
    proyecto_cal = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[not(@class) and not(@style)][4]/text()')
    ce_cal_src = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[position() = (last()-2)]/div/img/@src')
    cee_cal_src = parsed.xpath(
        '//table[@id="ContentPlaceHolder1_grdViviendasCal"]/tbody/tr/td[position() = (last()-1)]/div/img/@src')

    # Get the calification letter from src string
    ce_cal = [x.split('Letra')[1].split('.png')[0] for x in ce_cal_src]
    cee_cal = [x.split('Letra')[1].split('.png')[0] for x in cee_cal_src]

    # Creating a dictionary in order to create a dataframe
    if message_found_cal:
        # print(
        #     f'{message_found_cal[0]} {message_found_cal[1]} {message_found_cal[-1]}')
        vivienda_cal_dict = dict(zip(table_columns_cal, [
                                 vivienda_Id_cal, tipologia_cal, comuna_proyecto_cal, proyecto_cal, ce_cal, cee_cal]))
    else:
        # print(f'{message_not_found_cal[0]}')
        vivienda_cal_dict = dict(
            zip(table_columns_cal, [[], [], [], [], [], []]))
    viviendas_cal_df = pd.DataFrame.from_dict(data=vivienda_cal_dict)
    return viviendas_cal_df


def all_pages_precalificacion(region, comuna):
    eventtarget = 'ctl00$ContentPlaceHolder1$grdViviendasPre'
    eventargument = 'Page$1'
    # region = '10'
    # comuna = '234'
    certification = '1'     # Precalification: 1 / Calificacion: 2 / Both: '-1'
    # ----------
    pagination = True
    initial_round = True

    # -------
    # Request processing
    main_df = pd.DataFrame()
    while pagination:
        try:
            if initial_round:
                page_number = 1
                eventargument = 'Page$1'
                response = get_single_page_response(
                    eventtarget, eventargument, region, comuna, certification)
                home = response.content.decode('utf-8')
                parsed = html.fromstring(home)
                # Messages for found (or not found) dwellings
                message_found_pre = parsed.xpath(
                    '//strong/span[@id="ContentPlaceHolder1_ResultadoGrillaPre"]/descendant-or-self::*/text()')
                if message_found_pre:
                    number_of_pages = math.ceil(int(message_found_pre[1])/10)
                    # number_of_pages = 2
                    print(
                        f'{message_found_pre[0]} {message_found_pre[1]} {message_found_pre[-1]}')
                    initial_round = False

                else:
                    message_not_found_pre = parsed.xpath(
                        '//span[@id="ContentPlaceHolder1_grdViviendasPre_Label21"]/text()')
                    print(f'{message_not_found_pre[0]}')
                    break
            else:
                page_number += 1
                if page_number <= number_of_pages:
                    eventargument = 'Page$' + str(page_number)
                    response = get_single_page_response(
                        eventtarget, eventargument, region, comuna, certification)
                else:
                    break
            # Creating dataframes
            print(f'- Page {page_number} out of {number_of_pages}')
            viviendas_pre_df = single_page_precalificacion(response)
            main_df = pd.concat([main_df, viviendas_pre_df])

        except:
            pagination = False
            print('Failed !!!')
            path = './datasets/' + str(region) + '/'
            if not os.path.exists(path):
                os.makedirs(path)

            filename = region + "_" + comuna + "_" + certification + '_failed.txt'
            f = open(path+filename, "w+")
            f.write(
                f'The procces stopped at {page_number} out of {number_of_pages}')
            f.close()

    # Cleaning
    # Removing duplicates
    main_df.drop_duplicates(inplace=True)
    # Reseting indexes
    main_df.reset_index(drop=True, inplace=True)
    # Formating
    to_save_df = main_df.copy()
    # Saving data into a local folder or database
    path = '../data/raw/' + str(region) + '/'
    if not os.path.exists(path):
        os.makedirs(path)

    filename = region + "_" + comuna + "_" + certification + '.csv'
    print(f'Saving {filename} file')
    to_save_df.to_csv(path+filename, index=False, encoding="utf-8-sig")


def all_pages_calificacion(region, comuna):
    eventtarget = 'ctl00$ContentPlaceHolder1$grdViviendasCal'
    eventargument = 'Page$1'
    # region = '10'
    # comuna = '234'
    certification = '2'     # Precalification: 1 / Calificacion: 2 / Both: '-1'
    # ----------
    pagination = True
    initial_round = True

    # -------
    # Request processing
    main_df = pd.DataFrame()
    while pagination:
        try:
            if initial_round:
                page_number = 1
                eventargument = 'Page$1'
                response = get_single_page_response(
                    eventtarget, eventargument, region, comuna, certification)
                home = response.content.decode('utf-8')
                parsed = html.fromstring(home)
                # Messages for found (or not found) dwellings
                message_found_cal = parsed.xpath(
                    '//strong/span[@id="ContentPlaceHolder1_ResultadoGrillaCal"]/descendant-or-self::*/text()')
                if message_found_cal:
                    number_of_pages = math.ceil(int(message_found_cal[1])/10)
                    # number_of_pages = 2
                    print(
                        f'{message_found_cal[0]} {message_found_cal[1]} {message_found_cal[-1]}')
                    initial_round = False

                else:
                    message_not_found_cal = parsed.xpath(
                        '//span[@id="ContentPlaceHolder1_grdViviendasCal_Label21"]/text()')
                    print(f'{message_not_found_cal[0]}')
                    break
            else:
                page_number += 1
                if page_number <= number_of_pages:
                    eventargument = 'Page$' + str(page_number)
                    response = get_single_page_response(
                        eventtarget, eventargument, region, comuna, certification)
                else:
                    break
            # Creating dataframes
            print(f'- Page {page_number} out of {number_of_pages}')
            viviendas_cal_df = single_page_calificacion(response)
            main_df = pd.concat([main_df, viviendas_cal_df])

        except:
            pagination = False
            print('Failed !!!')
            path = './datasets/' + str(region) + '/'
            if not os.path.exists(path):
                os.makedirs(path)

            filename = region + "_" + comuna + "_" + certification + '_failed.txt'
            f = open(path+filename, "w+")
            f.write(
                f'The procces stopped at {page_number} out of {number_of_pages}')
            f.close()

    # Cleaning
    # Removing duplicates
    main_df.drop_duplicates(inplace=True)
    # Reseting indexes
    main_df.reset_index(drop=True, inplace=True)
    # Formating
    to_save_df = main_df.copy()
    # Saving data into a local folder or database
    path = '../data/raw/' + str(region) + '/'
    if not os.path.exists(path):
        os.makedirs(path)

    filename = region + "_" + comuna + "_" + certification + '.csv'
    print(f'Saving {filename} file')
    to_save_df.to_csv(path+filename, index=False, encoding="utf-8-sig")


def run(region):
    start_time = time()
    # get_regions()
    # get_cities_per_region(link=HOME_URL)
    # eventtarget = 'ctl00$ContentPlaceHolder1$grdViviendasPre'
    # eventargument = 'Page$1'
    # region = '6'
    with open('../json_files/cities_per_region.json') as json_file:
        cities_per_region_dict = json.load(json_file)
    cities_per_region = cities_per_region_dict[region]

    with open('../json_files/cities.json') as json_file:
        cities_dict = json.load(json_file)
    with open('../json_files/regions.json') as json_file:
        regions_dict = json.load(json_file)

    for comuna in cities_per_region:
        # comuna = '6'
        # certification = '-1'     # Precalification: 1 / Calificacion: 2 / Both: '-1'
        print('\n-------------------------------------')
        print(f'{regions_dict[region]}')
        print(f'Comuna: {cities_dict[comuna]}')
        print('-------------------------------------')

        all_pages_precalificacion(region, comuna)
        all_pages_calificacion(region, comuna)

    elapsed_time = time() - start_time
    print("\nElapsed time: %0.2f seconds." % elapsed_time)


def main(regions):
    start_time = time()
    for region in regions:
        run(region)
    elapsed_time = time() - start_time
    print("\nElapsed time: %0.2f seconds." % elapsed_time)


if __name__ == '__main__':

    # regions = ['1', '2', '3', '4', '5', '6', '7', '8',
    #    '9', '10', '11', '12', '13', '14', '15', '16']
    regions = ['15']
    main(regions)
