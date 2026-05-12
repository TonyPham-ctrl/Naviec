from fetch_aemo import *
import glob

time = dt.datetime(2017,1,1,0,0,0)


fetcher = NEMDataFetcher()
# fetcher.fetch_and_store(start_time=time, end_time=time+dt.timedelta(days=1), table='DISPATCHPRICE')

date_path = time.strftime('%Y/%m/%d') 
csv_files = glob.glob(os.path.join(fetcher.datapath, '*.CSV'))

df = pd.concat([pd.read_csv(f, header=1) for f in csv_files], ignore_index=True)
# df=df[['SETTLEMENTDATE','REGIONID','RRP']]
df = df[['SETTLEMENTDATE', 'REGIONID', 'RRP', 'APCFLAG', 'INTERVENTION']]
df.sort_values(by='REGIONID',inplace=True)
print(df)

# with open(file=file_path, mode='r') as fin:
    # data=fin.read().splitlines(True)

# with open(file=new_path, mode='w') as fout:
    # fout.writelines(data[1:])

# df=pd.read_csv(csv_file, sep=',')
# print(df)


# df=pd.read_csv()




# files = fetcher.fetch_and_store(
    # start_time = time,
    # end_time = time+dt.timedelta(minutes=5),
    # table = 'DISPATCHPRICE',
# )
