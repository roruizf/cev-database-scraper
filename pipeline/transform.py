import os
import pandas as pd
from datetime import datetime


def main():
    data_df = _read_data_files()
    data_df = _check_corrupt_ratings(data_df, 'CE')
    data_df = _check_corrupt_ratings(data_df, 'CEE')
    data_df = _drop_duplicates(data_df)
    data_df = _translate_column_region(data_df)
    data_df = _translate_column_status(data_df)
    data_df = _reorder_columns(data_df)
    _save_transformed_data(data_df)
    print(data_df.head())


def _read_data_files():
    dataset_path = "../data/raw/"
    folders_names = os.listdir(dataset_path)
    folders_names.sort(key=float)
    country_data_df = pd.DataFrame([], columns=[
        'Identificación Vivienda', 'Tipología', 'Comuna', 'Proyecto', 'CE', 'CEE', 'Informe', 'Etiqueta'])

    for folder_name in folders_names:
        folder_path = os.path.join(dataset_path, folder_name)

        # Looking for 'files' in folder_path
        files = os.listdir(folder_path)
        data_files = pd.Series(files)
        data_files_list = data_files[data_files.str.endswith('.csv')].to_list()

        region_data_df = pd.DataFrame([], columns=[
            'Identificación Vivienda', 'Tipología', 'Comuna', 'Proyecto', 'CE', 'CEE', 'Informe', 'Etiqueta'])
        for file in data_files_list:
            csv_file_name = file
            csv_file_path = os.path.join(folder_path, csv_file_name)
            file_name_wth_ext = os.path.splitext(
                csv_file_name)[0]  # filename without extension .csv
            region = file_name_wth_ext.split('_')[0]
            comuna = file_name_wth_ext.split('_')[1]
            certification = file_name_wth_ext.split('_')[2]

            try:
                data_df_i = pd.read_csv(csv_file_path, encoding='utf-8')
                # Add column "Region"
                data_df_i['Región'] = str(region)
                # Add column "Status"
                data_df_i['Status'] = str(certification)

            except pd.errors.EmptyDataError:
                data_df_i = pd.DataFrame([])

            region_data_df = pd.concat([region_data_df, data_df_i],
                                       ignore_index=True, sort=False)

        country_data_df = pd.concat([country_data_df, region_data_df],
                                    ignore_index=True, sort=False)
    return country_data_df


def _check_corrupt_ratings(data_df, column):
    ratings = ['A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'I']
    rows = data_df[~data_df[column].isin(ratings)]
    data_df.loc[rows.index, column] = 'N/A'
    # print(data_df.loc[rows.index, column])
    return data_df


def _drop_duplicates(data_df):
    # Only if all rows are repeated
    print(f'Number of rows BEFORE dropping duplicates: {data_df.shape[0]}')
    data_df = data_df.drop_duplicates(keep='last').reset_index(drop=True)
    print(f'Number of rows AFTER dropping duplicates: {data_df.shape[0]}')
    return data_df


def _translate_column_region(data_df):
    regions_dict = {'1': 'Tarapacá',
                    '2': 'Antofagasta',
                    '3': 'Atacama',
                    '4': 'Coquimbo',
                    '5': 'Valparaíso',
                    '6': "O'Higgins",
                    '7': 'Maule',
                    '8': 'Biobío',
                    '9': 'Araucanía',
                    '10': 'Los Lagos',
                    '11': 'Aysén',
                    '12': 'Magallanes',
                    '13': 'Metropolitana',
                    '14': 'Los Ríos',
                    '15': 'Arica y Parinacota',
                    '16': 'Ñuble'}
    data_df['Región'] = data_df['Región'].astype(str)
    data_df['Región'] = data_df['Región'].map(regions_dict)
    return data_df


def _translate_column_status(data_df):
    certification_dict = {"1": 'Pre-calificación',
                          "2": 'Calificación'}
    data_df['Status'] = data_df['Status'].astype(str)
    data_df['Status'] = data_df['Status'].map(certification_dict)
    return data_df


def _reorder_columns(data_df):
    data_df = data_df[['Identificación Vivienda', 'Proyecto',
                       'Tipología', 'Comuna',  'Región', 'Status', 'CE', 'CEE', 'Informe', 'Etiqueta']]
    return data_df


def _save_transformed_data(data_df):
    today = datetime.now()
    today_date = today.strftime("%Y-%B")

    # Remove previous saved files if they exist...
    remove_existing_files()

    # Save data...

    print(f"Saving TRANSFORMED data CEV-Chile-{today_date}.")

    data_df_csv_name = f"../data/interim/CEV-Chile-{today_date}.csv"
    data_df.to_csv(data_df_csv_name, sep=',',
                   index=False, encoding='utf-8-sig')


def remove_existing_files(destination_directory_path='../data/interim/'):
    # check destination_directory_path is empty
    files_in_directory = os.listdir(destination_directory_path)
    print(f"\nRemoving EXISTING files...")
    if len(files_in_directory) != 0:  # -> directory is NOT empty then delete those files
        # print(files_in_directory)
        for file in files_in_directory:
            os.remove(os.path.join(destination_directory_path, file))
            print(f'- File {file} deleted!')


if __name__ == '__main__':
    main()
