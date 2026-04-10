import pandas as pd
import sqlite3

def duplicate_links():
    conn = sqlite3.connect('refdb.db')

    with open('track_changes.sql', 'r', encoding='utf-8') as fhandle:
        sql_command = fhandle.read()

    df = pd.read_sql(sql_command, conn)

    unique_links = df.Link.drop_duplicates()

    output_df = pd.DataFrame()

    for link in unique_links:
        df_filtered = df[df.Link == link]
        output_str = ''

        if len(set(list(df_filtered.Price))) > 1:
            output_str = '<br>'.join([f'{x[1].StudyDate}:    EUR {x[1].Price:.0f}' for x in df_filtered.iterrows()])

        # for idx, row in list(df_filtered.iterrows())[1:]:


            # if df_filtered.loc[idx - 1].Price != row.Price:
            #     output_str += f"{row.StudyDate}: cena {'palielināta' if row.Price >  df_filtered.loc[idx-1].Price else 'samazināta'} no {df_filtered.loc[idx-1].StudyDate} cenas EUR {df_filtered.loc[idx-1].Price:.0f} uz EUR {row.Price:.0f}.\n"
        output_df = pd.concat([output_df, pd.DataFrame(columns=['Link', 'Description'], data=[[link, output_str]])])

    conn.close()
    return output_df.set_index('Link')

price_changes = duplicate_links()

def get_all_rows(study_date, typeofdeal, city=None, district=None, price_changes_only=False):
    conn = sqlite3.connect('refdb.db')

    sql_basic = f"""
    with t1 as (
    
    SELECT
    
    Datums.StudyDate,
    COALESCE(RealEstateOverride.Link, RealEstate.Link) as Link,
    COALESCE(RealEstateOverride.TypeOfDeal, RealEstate.TypeOfDeal) as TypeOfDeal,
    COALESCE(RealEstateOverride.Cena, RealEstate.Cena) as Price,
    COALESCE(RealEstateOverride.Izmers, RealEstate.Izmers) as Size,
    COALESCE(RealEstateOverride.Stavs, RealEstate.Stavs) as Flr,
    COALESCE(RealEstateOverride.ErtibasId, RealEstate.ErtibasId) as ErtibasId,
    COALESCE(RealEstateOverride.MajasTipsId, RealEstate.MajasTipsId) as MajasTipsId,
    COALESCE(RealEstateOverride.SerijaId, RealEstate.SerijaId) as SerijaId,
    
    COALESCE(RealEstateOverride.Cena, RealEstate.Cena) / COALESCE(RealEstateOverride.Izmers, RealEstate.Izmers) as Per_sqm,
    
    COALESCE(RealEstateOverride.PilsetaId, RealEstate.PilsetaId) as PilsetaId,
    COALESCE(RealEstateOverride.RajonsId, RealEstate.RajonsId) as RajonsId,
    COALESCE(RealEstateOverride.IelaId, RealEstate.IelaId) as IelaId
    
    
    From Ad
    left join Datums on Ad.DatumsId = Datums.Id
    left join RealEstate on Ad.RealEstateId = RealEstate.Id
    left join RealEstateOverride on Ad.RealEstateId = RealEstateOverride.RealEstateId
    
    where Datums.StudyDate = '{study_date}'
    ),
    
    t2 as (
    
    select t1.StudyDate,
    t1.Link,
    t1.TypeOfDeal,
    t1.Price,
    t1.Size,
    t1.Flr,
    t1.ErtibasId,
    MajasTips.Name as BuildigType,
    Serija.Name as Series,
    t1.Per_sqm,
    Pilseta.Name as City,
    Rajons.Name as District,
    Iela.Name as Street
    
    from t1
    left join MajasTips on t1.MajasTipsId = MajasTips.Id
    left join Serija on t1.SerijaId = Serija.Id
    left join Pilseta on t1.PilsetaId = Pilseta.Id
    left join Rajons on t1.RajonsId = Rajons.Id
    left join Iela on t1.IelaId = Iela.Id
    
    where t1.TypeOfDeal = {str(typeofdeal)}
    )
    
    select t2.*
    from t2
    
    where t2.City not in ('nan', 'None')
    and t2.District not in ('nan', 'None')
    
    {"and t2.City = '" + city + "'" if city is not None else ''}
    {"and t2.District = '" + district + "'" if district is not None else ''}

    """

    ertibas_ids = pd.read_sql('SELECT * FROM Ertibas', conn).set_index('Id')

    def decode_ertibas(row):
        ertibas_bin = bin(row.ErtibasId)[2:]
        str_output = []
        for i in range(len(ertibas_bin)):
            idx = (i+1)*(-1)
            if ertibas_bin[idx] == '0':
                continue
            str_output.append(ertibas_ids.loc[idx*(-1)]['Name'])

        str_output = ', '.join(str_output)

        return str_output if len(str_output) > 0 else None

    re_df = pd.read_sql(sql_basic, conn)
    re_df['Ertibas'] = re_df.apply(decode_ertibas, axis=1)


    def create_custom_text(row):
        output_str = ''
        output_str += f'Platība:        {row.Size:.0f} m<sup>2</sup><br>'
        output_str += f'Cena:       EUR {row.Price:.0f} {"/ mēnesī" if row.TypeOfDeal == 0 else ''}<br>'
        output_str += f'Sērija:     {row.Series}<br>'
        output_str += f'Mājas Tips:     {row.BuildigType}<br>'
        output_str += f'Stāvs:      {row.Flr}<br>'
        if not pd.isna(row.Ertibas):
            output_str += f'Ērtības:        {row.Ertibas}<br>'

        try:
            if price_changes.loc[row.Link].Description != '':
                output_str += '<br>Cenas izmaiņas:<br>'+ price_changes.loc[row.Link].Description
        except KeyError:
            pass
        output_str += '<br><br><br>'
        output_str += f'<a href="https://www.ss.lv/msg/lv/real-estate/flats/{row.Link}">Apskatīt sludinājumu</a><br>'
        return output_str


    re_df['custom_text'] = re_df.apply(create_custom_text, axis=1)

    conn.close()
    return re_df if not price_changes_only else re_df[re_df.custom_text.str.contains('Cenas izmaiņas:<br>')]

def avg_price_timeline(typeofdeal: int):
    conn = sqlite3.connect('refdb.db')

    sql_command = f"""
            with t1 as (
    
    SELECT
    
    Datums.StudyDate,
    COALESCE(RealEstateOverride.Link, RealEstate.Link) as Link,
    COALESCE(RealEstateOverride.TypeOfDeal, RealEstate.TypeOfDeal) as TypeOfDeal,
    COALESCE(RealEstateOverride.Cena, RealEstate.Cena) as Price,
    COALESCE(RealEstateOverride.Izmers, RealEstate.Izmers) as Size,
    COALESCE(RealEstateOverride.Stavs, RealEstate.Stavs) as Flr,
    COALESCE(RealEstateOverride.ErtibasId, RealEstate.ErtibasId) as ErtibasId,
    COALESCE(RealEstateOverride.MajasTipsId, RealEstate.MajasTipsId) as MajasTipsId,
    COALESCE(RealEstateOverride.SerijaId, RealEstate.SerijaId) as SerijaId,
    
    COALESCE(RealEstateOverride.Cena, RealEstate.Cena) / COALESCE(RealEstateOverride.Izmers, RealEstate.Izmers) as Per_sqm,
    
    COALESCE(RealEstateOverride.PilsetaId, RealEstate.PilsetaId) as PilsetaId,
    COALESCE(RealEstateOverride.RajonsId, RealEstate.RajonsId) as RajonsId,
    COALESCE(RealEstateOverride.IelaId, RealEstate.IelaId) as IelaId
    
    
    From Ad
    left join Datums on Ad.DatumsId = Datums.Id
    left join RealEstate on Ad.RealEstateId = RealEstate.Id
    left join RealEstateOverride on Ad.RealEstateId = RealEstateOverride.RealEstateId
    
    --where Datums.StudyDate = '2026-03-07'
    ),
    
    t2 as (
    
    select t1.StudyDate,
    t1.Link,
    t1.TypeOfDeal,
    t1.Price,
    t1.Size,
    t1.Flr,
    t1.ErtibasId,
    MajasTips.Name as BuildigType,
    Serija.Name as Series,
    t1.Per_sqm,
    Pilseta.Name as City,
    Rajons.Name as District,
    Iela.Name as Street
    
    from t1
    left join MajasTips on t1.MajasTipsId = MajasTips.Id
    left join Serija on t1.SerijaId = Serija.Id
    left join Pilseta on t1.PilsetaId = Pilseta.Id
    left join Rajons on t1.RajonsId = Rajons.Id
    left join Iela on t1.IelaId = Iela.Id
    
    where t1.TypeOfDeal = {str(typeofdeal)}
    ),

    t3 as (
    
    select t2.StudyDate, t2.City, round(SUM(t2.Price) / SUM(t2.Size), 2) as WeightedAvg
    from t2
    
    where t2.City not in ('nan', 'None')
    and t2.District not in ('nan', 'None')
    
    group by t2.StudyDate, t2.City
    
    
    order by t2.StudyDate, SUM(t2.Price) / SUM(t2.Size)
    ),

    t4 as (
    select t2.StudyDate, 'Total' as City, round(SUM(t2.Price) / SUM(t2.Size), 2) as WeightedAvg
    from t2
    
    where t2.City not in ('nan', 'None')
    and t2.District not in ('nan', 'None')
    
    group by t2.StudyDate
    
    
    order by t2.StudyDate, SUM(t2.Price) / SUM(t2.Size)
    )

    select t3.* from t3
    union
    select t4.* from t4
    order by StudyDate


        """
    df = pd.read_sql(sql_command, conn)
    df['StudyDate'] = pd.to_datetime(df['StudyDate'])

    return df.pivot(index='StudyDate', columns='City', values='WeightedAvg')


def volume_timeline():
    conn = sqlite3.connect('refdb.db')

    sql_command = """
            with t1 as (

    SELECT

    Datums.StudyDate,
    COALESCE(RealEstateOverride.Link, RealEstate.Link) as Link,
    COALESCE(RealEstateOverride.TypeOfDeal, RealEstate.TypeOfDeal) as TypeOfDeal,
    COALESCE(RealEstateOverride.Cena, RealEstate.Cena) as Price,
    COALESCE(RealEstateOverride.Izmers, RealEstate.Izmers) as Size,
    COALESCE(RealEstateOverride.Stavs, RealEstate.Stavs) as Flr,
    COALESCE(RealEstateOverride.ErtibasId, RealEstate.ErtibasId) as ErtibasId,
    COALESCE(RealEstateOverride.MajasTipsId, RealEstate.MajasTipsId) as MajasTipsId,
    COALESCE(RealEstateOverride.SerijaId, RealEstate.SerijaId) as SerijaId,

    COALESCE(RealEstateOverride.Cena, RealEstate.Cena) / COALESCE(RealEstateOverride.Izmers, RealEstate.Izmers) as Per_sqm,

    COALESCE(RealEstateOverride.PilsetaId, RealEstate.PilsetaId) as PilsetaId,
    COALESCE(RealEstateOverride.RajonsId, RealEstate.RajonsId) as RajonsId,
    COALESCE(RealEstateOverride.IelaId, RealEstate.IelaId) as IelaId


    From Ad
    left join Datums on Ad.DatumsId = Datums.Id
    left join RealEstate on Ad.RealEstateId = RealEstate.Id
    left join RealEstateOverride on Ad.RealEstateId = RealEstateOverride.RealEstateId

    --where Datums.StudyDate = '2026-03-07'
    ),

    t2 as (

    select t1.StudyDate,
    t1.Link,
    t1.TypeOfDeal,
    t1.Price,
    t1.Size,
    t1.Flr,
    t1.ErtibasId,
    MajasTips.Name as BuildigType,
    Serija.Name as Series,
    t1.Per_sqm,
    Pilseta.Name as City,
    Rajons.Name as District,
    Iela.Name as Street

    from t1
    left join MajasTips on t1.MajasTipsId = MajasTips.Id
    left join Serija on t1.SerijaId = Serija.Id
    left join Pilseta on t1.PilsetaId = Pilseta.Id
    left join Rajons on t1.RajonsId = Rajons.Id
    left join Iela on t1.IelaId = Iela.Id

    where t1.TypeOfDeal = 0
    )

    select t2.StudyDate, t2.City, t2.District, round(SUM(t2.Size), 2) as TotalSize
    from t2

    where t2.City not in ('nan', 'None')
    and t2.District not in ('nan', 'None')

    group by t2.StudyDate, t2.City, t2.District


    order by t2.StudyDate, SUM(t2.Size)


        """
    df = pd.read_sql(sql_command, conn)
    df['StudyDate'] = pd.to_datetime(df['StudyDate'])

    df['Location'] = df.City + ', ' + df.District
    return df.pivot(index='StudyDate', columns='Location', values='TotalSize')

def get_static(table_name):
    with sqlite3.connect('refdb.db') as conn:

        static_data = list(pd.read_sql(f"select Name from {table_name} where Name not in ('None', 'nan')", conn)['Name'])

    return static_data


def get_dates():
    with sqlite3.connect('refdb.db') as conn:

        sql_dates = list(pd.read_sql("SELECT * from Datums order by Id", conn).StudyDate)

    return sql_dates[0], sql_dates[-1]
