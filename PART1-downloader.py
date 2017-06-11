# Prgramitically Log in to Freddie Mac Webisite and download all the files based on request
import requests
import re
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO
import time
import datetime
import sys
from tqdm import tqdm
import pandas as pd
import numpy as np
import glob
import csv

url='https://freddiemac.embs.com/FLoan/secure/auth.php'
postUrl='https://freddiemac.embs.com/FLoan/Data/download.php'

def payloadCreation(user, passwd):
    creds={'username': user,'password': passwd}
    return creds

def assure_path_exists(path):
    if not os.path.exists(path):
            os.makedirs(path)

def extracrtZip(s,monthlistdata,path):
    abc = tqdm(monthlistdata)
    for month in abc:
        abc.set_description("Downloading %s" % month)
        r = s.get(month)
        z = ZipFile(BytesIO(r.content)) 
        z.extractall(path)    

def getFilesFromFreddieMac(payload,st,en):
    with requests.Session() as s:
        preUrl = s.post(url, data=payload)  
        payload2={'accept': 'Yes','acceptSubmit':'Continue','action':'acceptTandC'}
        finalUrl=s.post(postUrl,payload2)
        linkhtml =finalUrl.text 
        allzipfiles=BeautifulSoup(linkhtml, "html.parser")
        ziplist=allzipfiles.find_all('td')
        sampledata=[]
        historicaldata=[]
        count=0
        slist=[]
        for i in range(int(st),int(en)+1):
            #print(i)
            slist.append(i)
        for li in ziplist:
            zipatags=li.findAll('a')
            for zipa in zipatags:
                for yr in slist:
                    if str(yr) in zipa.text:
                        if re.match('sample',zipa.text):
                            link = zipa.get('href')
                            foldername= 'SampleInputFiles'
                            Samplepath=str(os.getcwd())+"/"+foldername
                            assure_path_exists(Samplepath)
                            finallink ='https://freddiemac.embs.com/FLoan/Data/' + link
                            sampledata.append(finallink) 
        extracrtZip(s,sampledata,Samplepath)


def fillNAN(df):
    df['fico'] = df['fico'].fillna(0)
    df['flag_fthb']=df['flag_fthb'].fillna('X')
    df['cd_msa']=df['cd_msa'].fillna(0)
    df['mi_pct']=df['mi_pct'].fillna(0)
    df['cnt_units']=df['cnt_units'].fillna(0)
    df['occpy_sts']=df['occpy_sts'].fillna('X')
    df['cltv']=df['cltv'].fillna(0)
    df['dti']=df['dti'].fillna(0)
    df['ltv']=df['ltv'].fillna(0)
    df['channel']=df['channel'].fillna('X')
    df['ppmt_pnlty']=df['ppmt_pnlty'].fillna('X')
    df['prop_type']=df['prop_type'].fillna('XX')
    df['zipcode']=df['zipcode'].fillna(0)
    df['loan_purpose']=df['loan_purpose'].fillna('X')
    df['cnt_borr']=df['cnt_borr'].fillna(0)
    df['flag_sc']=df['flag_sc'].fillna('N')
    return df

def changedatatype(df):
    #Change the data types for all column
    df[['fico','cd_msa','mi_pct','cnt_borr','cnt_units','cltv','dti','orig_upb','ltv','zipcode','orig_loan_term']] = df[['fico','cd_msa','mi_pct','cnt_borr','cnt_units','cltv','dti','orig_upb','ltv','zipcode','orig_loan_term']].astype('int64')
    df[['flag_sc','servicer_name']] = df[['flag_sc','servicer_name']].astype('str')
    return df

def fillNA(df):
    df['delq_sts'] = df['delq_sts'].fillna(0)
    df['repch_flag']=df['repch_flag'].fillna('X')
    df['flag_mod']=df['flag_mod'].fillna('N')
    df['cd_zero_bal']=df['cd_zero_bal'].fillna(00)
    df['dt_zero_bal']=df['dt_zero_bal'].fillna('189901')
    df['non_int_brng_upb']=df['non_int_brng_upb'].fillna(0)
    df['dt_lst_pi']=df['dt_lst_pi'].fillna('189901')
    df['mi_recoveries']=df['mi_recoveries'].fillna(0)
    df['net_sale_proceeds']=df['net_sale_proceeds'].fillna('U')
    df['non_mi_recoveries']=df['non_mi_recoveries'].fillna(0)
    df['expenses']=df['expenses'].fillna(0)
    df['legal_costs']=df['legal_costs'].fillna(0)
    df['maint_pres_costs']=df['maint_pres_costs'].fillna(0)
    df['taxes_ins_costs']=df['taxes_ins_costs'].fillna(0)
    df['misc_costs']=df['misc_costs'].fillna(0)
    df['actual_loss']=df['actual_loss'].fillna(0)
    df['modcost']=df['modcost'].fillna(0)
    return df

def changedtype(df):
    #Change the data types for all column
    df[['loan_age','mths_remng','cd_zero_bal','non_int_brng_upb','delq_sts','actual_loss']] = df[['loan_age','mths_remng','cd_zero_bal','non_int_brng_upb','delq_sts','actual_loss']].astype('int64')
    df[['svcg_cycle','dt_zero_bal','dt_lst_pi']] = df[['svcg_cycle','dt_zero_bal','dt_lst_pi']].astype('str')
    return df

def get_current_upb(group):
    return {'min_current_upb': group.min(), 'max_current_upb': group.max()}
def get_delq_sts(group):
    return {'min_delq_sts': group.min(), 'max_delq_sts': group.max()}
def get_cd_zero_bal(group):
    return {'min_cd_zero_bal': group.min(), 'max_cd_zero_bal': group.max()}
def get_mi_recoveries(group):
    return {'min_mi_recoveries': group.min(), 'max_mi_recoveries': group.max()}
def get_net_sale_proceeds(group):
    return { 'min_net_sale_proceeds': group.min(), 'max_net_sale_proceeds': group.max()}
def get_non_mi_recoveries(group):
    return {'min_non_mi_recoveries': group.min(), 'max_non_mi_recoveries': group.max()}
def get_expenses(group):
    return {'min_expenses': group.min(), 'max_expenses': group.max()}
def get_legal_costs(group):
    return {'min_legal_costs': group.min(), 'max_legal_costs': group.max()}
def get_maint_pres_costs(group):
    return {'min_maint_pres_costs': group.min(), 'max_maint_pres_costs': group.max()}
def get_taxes_ins_costs(group):
    return {'min_taxes_ins_costs': group.min(), 'max_taxes_ins_costs': group.max()}
def get_misc_costs(group):
    return {'min_misc_costs': group.min(), 'max_misc_costs': group.max()}
def get_actual_loss(group):
    return {'min_actual_loss': group.min(), 'max_actual_loss': group.max()}
def get_modcost(group):
    return {'min_modcost': group.min(), 'max_modcost': group.max()}


#Create a data frame for all 18 Origination files
#code originated file
def createOriginationCombined(str):
    #print(str)
    writeHeader1 = True
    if "sample" in str:
        filename= "SampleOriginationCombined.csv"
    else:
        filename= "HistoricalOriginationCombined.csv"
    
    abc = tqdm(glob.glob(str))
      
    with open(filename, 'w',encoding='utf-8',newline="") as file:
        for f in abc: 
            abc.set_description("Working on  %s" % f)
            sample_df = pd.read_csv(f ,sep="|", names=['fico','dt_first_pi','flag_fthb','dt_matr','cd_msa',"mi_pct",'cnt_units','occpy_sts','cltv','dti','orig_upb','ltv','int_rt','channel','ppmt_pnlty','prod_type','st', 'prop_type','zipcode','id_loan','loan_purpose', 'orig_loan_term','cnt_borr','seller_name','servicer_name','flag_sc'],skipinitialspace=True) 
            sample_df = fillNAN(sample_df)
            sample_df = changedatatype(sample_df)
            sample_df['Year'] = ['19'+x if x=='99' else '20'+x for x in (sample_df['id_loan'].apply(lambda x: x[2:4]))]
            if writeHeader1 is True:    
                sample_df.to_csv(file, mode='a', header=True,index=False)
                writeHeader1 = False
            else:
                sample_df.to_csv(file, mode='a', header=False,index=False)

def createPerformanceCombined(str): 
    print(str)
    writeHeader2 = True
    if "sample" in str:
        filename= "SamplePerformanceCombinedSummary.csv"
    else:
        filename= "HistoricalPerformanceCombinedSummary.csv"
    
    abc = tqdm(glob.glob(str))
 
    with open(filename, 'w',encoding='utf-8',newline="") as file:
        for f in abc: 
            abc.set_description("Working on  %s" % f)
            perf_df = pd.read_csv(f ,sep="|", names=['id_loan','svcg_cycle','current_upb','delq_sts','loan_age','mths_remng', 'repch_flag','flag_mod', 'cd_zero_bal', 'dt_zero_bal','current_int_rt','non_int_brng_upb','dt_lst_pi','mi_recoveries', 'net_sale_proceeds','non_mi_recoveries','expenses', 'legal_costs', 'maint_pres_costs','taxes_ins_costs','misc_costs','actual_loss', 'modcost'],skipinitialspace=True) 
            perf_df['delq_sts'] = [ 999 if x=='R' else x for x in (perf_df['delq_sts'].apply(lambda x: x))]
            perf_df['delq_sts'] = [ 0 if x=='XX' else x for x in (perf_df['delq_sts'].apply(lambda x: x))]
            perf_df = fillNA(perf_df)
            perf_df = changedtype(perf_df)
            summ_df = pd.DataFrame()
            summ_df['id_loan']= perf_df['id_loan'].drop_duplicates()
            summ_df=summ_df.join((perf_df['current_upb'].groupby(perf_df['id_loan']).apply(get_current_upb).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['delq_sts'].groupby(perf_df['id_loan']).apply(get_delq_sts).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['cd_zero_bal'].groupby(perf_df['id_loan']).apply(get_cd_zero_bal).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['non_mi_recoveries'].groupby(perf_df['id_loan']).apply(get_non_mi_recoveries).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['expenses'].groupby(perf_df['id_loan']).apply(get_expenses).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['legal_costs'].groupby(perf_df['id_loan']).apply(get_legal_costs).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['maint_pres_costs'].groupby(perf_df['id_loan']).apply(get_maint_pres_costs).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['taxes_ins_costs'].groupby(perf_df['id_loan']).apply(get_taxes_ins_costs).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['misc_costs'].groupby(perf_df['id_loan']).apply(get_misc_costs).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['actual_loss'].groupby(perf_df['id_loan']).apply(get_actual_loss).unstack()),on='id_loan')
            summ_df=summ_df.join((perf_df['modcost'].groupby(perf_df['id_loan']).apply(get_modcost).unstack()),on='id_loan')
            if writeHeader2 is True:    
                summ_df.to_csv(file, mode='a', header=True,index=False)
                writeHeader2 = False
            else:
                summ_df.to_csv(file, mode='a', header=False,index=False)  
            


def main():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
    args = sys.argv[1:]
    print("Starting")
	    

    counter = 0
    if len(args) == 0:
        print("No input arguments..Exiting!")
        exit(0)
    for arg in args:
        if counter == 0:
            user = str(arg)
        elif counter == 1:
            passwd = str(arg)
        elif counter == 2:
            startYear = str(arg)
        else:
            endYear = str(arg)
        counter += 1

    print("USERNAME="+user)
    print("PASSWORD="+passwd)
    print("START YEAR="+(startYear))
    print("END YEAR="+(endYear))

    payload=payloadCreation(user,passwd)
    getFilesFromFreddieMac(payload,startYear,endYear) 
    foldername= 'SampleInputFiles'

    sampleOrigFiles=str(os.getcwd())+"/"+foldername+"/sample_orig_*.txt"
    samplePerfFiles=str(os.getcwd())+"/"+foldername+"/sample_svcg_*.txt"

    createOriginationCombined(sampleOrigFiles)
    createPerformanceCombined(samplePerfFiles)

if __name__ == '__main__':
    main()
