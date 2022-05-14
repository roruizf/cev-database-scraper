import os
import pandas as pd
import psycopg2
import psycopg2.extras as extras
import numpy as np


def main():
    data_df = _read_data_files()
    data_df = _set_columns_types(data_df)
    data_df = _check_corrupt_ratings(data_df, 'CE')
    data_df = _check_corrupt_ratings(data_df, 'CEE')
    conn = _connect_to_database()
    stored_data_df = _get_stored_index_list(conn)
    data_to_insert_df, data_to_upsert_df = _compare_stored_and_new_data(
        data_df, stored_data_df)
    _insert_values(conn, data_to_insert_df, 'home_ratings')
    _insert_values(conn, data_to_upsert_df, 'home_ratings')


def _read_data_files():
    dataset_path = "../data/interim/"
    files = os.listdir(dataset_path)
    # Looking for 'data-tender_list'
    data_files = pd.Series(files)
    data_files_list = data_files[data_files.str.endswith('.csv')].to_list()
    # Create a dataframe contaning from files in data_files_list
    data_df = pd.DataFrame([], columns=['Identificación Vivienda', 'Proyecto',
                                        'Tipología', 'Comuna', 'Región', 'Status', 'CE', 'CEE'])
    for file in data_files_list:
        csv_file_name = file
        csv_file_path = os.path.join(dataset_path, csv_file_name)
        data_df_i = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        data_df = pd.concat([data_df, data_df_i],
                            ignore_index=True, sort=False)
    return data_df


def _set_columns_types(data_df):
    data_df['Identificación Vivienda'] = data_df['Identificación Vivienda'].astype(
        str)
    data_df['Proyecto'] = data_df['Proyecto'].astype(str)
    data_df['Tipología'] = data_df['Tipología'].astype(str)
    data_df['Comuna'] = data_df['Comuna'].astype(str)
    data_df['Región'] = data_df['Región'].astype(str)
    data_df['Status'] = data_df['Status'].astype(str)
    data_df['CE'] = data_df['CE'].astype(str)
    data_df['CEE'] = data_df['CEE'].astype(str)
    return data_df


def _check_corrupt_ratings(data_df, column):
    ratings = ['A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'I']
    rows = data_df[~data_df[column].isin(ratings)]
    data_df.loc[rows.index, column] = None
    # print(data_df.loc[rows.index, column])
    return data_df


def _connect_to_database():
    # CONNECTION TO THE DATABASE
    try:
        conn = psycopg2.connect(
            host='host',
            port=5432,
            database="cev_home_ratings",
            user="postgres",
            password="mmTBhY#RzefXz94G",

        )

        print("Successful connection")
        #cursor = conn.cursor()
        #row = cursor.fetchone()
        # print(row)

    except Exception as ex:
        print(ex)
    return conn


def _get_stored_index_list(conn):
    sql_query = """
                SELECT identificacion_vivienda, proyecto, tipologia, comuna, region, status, ce, cee
	            FROM public.home_ratings;
                """
    stored_data_df = pd.io.sql.read_sql_query(sql_query, conn)
    return stored_data_df


def _compare_stored_and_new_data(data_df, stored_data_df):
    # data_df.columns = ['identificacion_vivienda',
    #                    'proyecto',
    #                    'tipologia',
    #                    'comuna',
    #                    'region',
    #                    'status',
    #                    'ce',
    #                    'cee']
    data_df = data_df.rename(columns={'Identificación Vivienda': 'identificacion_vivienda',
                                      'Tipología': 'tipologia',
                                      'Comuna': 'comuna',
                                      'Proyecto': 'proyecto',
                                      'CE': 'ce',
                                      'CEE': 'cee',
                                      'Región': 'region',
                                      'Status': 'status'})
    # print(data_df.columns)
    # print(stored_data_df.columns)
    # Getting common 'identificacion_vivienda'
    common_identificacion_vivienda = list(set(data_df['identificacion_vivienda'].to_list()) & set(
        stored_data_df['identificacion_vivienda'].to_list()))

    # Distinct 'identificacion_vivienda' rows -> this is new data
    data_to_insert_df = data_df[~data_df['identificacion_vivienda'].isin(
        common_identificacion_vivienda)].reset_index(drop=True)

    # # Mutual 'identificacion_vivienda' rows
    # mutual_data_df = data_df[data_df['identificacion_vivienda'].isin(
    #     common_identificacion_vivienda)].sort_values(by='identificacion_vivienda').reset_index(drop=True)
    # mutual_stored_data_df = stored_data_df[stored_data_df['identificacion_vivienda'].isin(
    #     common_identificacion_vivienda)].sort_values(by='identificacion_vivienda').reset_index(drop=True)
    # print(mutual_data_df['status'])
    # print(mutual_stored_data_df['status'])
    # common_status = (mutual_data_df['status'] ==
    #                  mutual_stored_data_df['status'])

    # # Distinct 'status' rows -> these data exist but 'status' have changed
    # data_to_upsert_df = mutual_data_df[~common_status]
    data_to_upsert_df = pd.DataFrame([])
    return data_to_insert_df, data_to_upsert_df


def _insert_values(conn, df, table):

    if not df.empty:

        tuples = [tuple(x) for x in df.to_numpy()]

        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
        print(query)
        cursor = conn.cursor()
        try:
            extras.execute_values(cursor, query, tuples)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("the dataframe is inserted")
        cursor.close()
    else:
        print('Nothing to INSERT')


if __name__ == '__main__':
    main()
