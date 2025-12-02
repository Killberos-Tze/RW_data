#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 18 16:19:18 2022

@author: tzework
"""
from numpy import array, linspace, savetxt, shape, swapaxes, sort
from os import path

#for loading a file you need first read function that reads it
#then you need process functions that are processing it
#they are called from loading function that is saying all is okay and gives data back to main script
#future inst file example
#ip_list:=192.168.1.210,192.168.1.220
#port_list:=5025,5025
#unitless quantities will have unit of "None"

ihtm_kword_sep=":="
ihtm_sep='\t'
coma_sep=','
column_sep=';'
sep_list=['\t',' ',',',':','\\']


ihtm_sections=['#comment',#never used in old ones here we put info about user and something about measurement
              '#setup',#never used in old ones here we should write about device, time, date, values
              '#sample',#for new files, here we should put into about sample name, area, number of cells, material,configuratrion
              '#data_header',#to remain compatible with old files
              '#data_summary',#for new files
              '#data_table']

ihtm_keywords=['load_file_path',
                 'save_file_path',
                 'ref_file_path',
                 'ref_file_name']
instr_keywords=['ip_address',
                 'port',
                 'device_name']


class Read_from():
    def uninova(filename):
        out={}
        out['error']=''
        out['#data_table']=[]
        out['#data_summary']={}
        out['#data_summary']['symbol_list']=['x1','y1']
        out['#data_summary']['x1_col']=0
        out['#data_summary']['y1_col']=1
        out['#data_summary']['x1_name']='wavelength'
        out['#data_summary']['y1_label']=path.basename(filename).split('.csv')[0]
        out['#data_summary']['y1_unit']=''
        try:
            with open(filename, 'r') as f:
                flag=False #only first line is some info
                for line in f:
                    tmp=line.strip()
                    if flag:
                        out['#data_table'].append(tmp.replace(',','.').split(column_sep))
                    else:
                        xunit,quantity=tmp.split(column_sep)
                        quantity=quantity.strip()
                        out['#data_summary']['x1_unit']=xunit[-1]
                        out['#data_summary']['x1_prefix']=xunit[0]
                        if quantity=='%R':
                            out['#data_summary']['y1_prefix']='c'
                            out['#data_summary']['y1_name']='Reflectance'
                        elif quantity=='%T':
                            out['#data_summary']['y1_prefix']='c'
                            out['#data_summary']['y1_name']='Transmittance'
                    flag=True #after first line it is finished
            out["#data_table"]=array(out["#data_table"]).astype(float)
            out["#data_table"]=out["#data_table"][out["#data_table"][:, 0].argsort()]
            out['#data_summary']['tot_row'],out['#data_summary']['tot_col']=shape(out["#data_table"])
        except:
            out['error']='File cannot be read!'
        return out

    def gwyddion_distribution(filename):
        out={}
        out['error']=''
        out['#data_table']=[]
        out['#data_summary']={}
        #out['#data_summary']['symbol_list']=['x1','y1']
        out['#data_summary']['y1_name']='Distribution'
        out['#data_summary']['x1_col']=0
        out['#data_summary']['y1_col']=1
        try:
            with open(filename, 'r') as f:
                cnt=0
                for line in f:
                    tmp=line.strip()
                    if cnt>2:
                        out['#data_table'].append(tmp.split())
                    elif cnt>1:
                        tmp=tmp.split()
                        if '<sup>' in tmp[1]:
                            unittmp=tmp[1][1:-1].replace('</sup>','}$').replace('<sup>','$^{')
                            out['#data_summary']['y1_power']=float(unittmp[unittmp.index('{')+1:unittmp.index('}')])
                        #for some case where you have <sub>
                        #if '<sub>' in tmp[1]:
                        #    unittmp=tmp[1][1:-1].replace('</sub>','}$').replace('<sub>','$^{')
                        out['#data_summary']['y1_unit']=unittmp[unittmp.index('$')-1:unittmp.index('$')]
                        out['#data_summary']['y1_prefix']=unittmp[0:unittmp.index('$')-1]
                        unittmp=tmp[0][1:-1]
                        out['#data_summary']['x1_prefix']=unittmp[0:-1]
                        out['#data_summary']['x1_unit']=unittmp[-1:]
                    elif cnt>0:
                        tmp=tmp.split()
                        out['#data_summary']['y1_name']=tmp[1]
                    cnt+=1
            out["#data_table"]=array(out["#data_table"]).astype(float)
            out['#data_summary']['tot_row'],out['#data_summary']['tot_col']=shape(out["#data_table"])
            if out['#data_summary']['x1_unit']=='m':
                out['#data_summary']['x1_name']='Height'
            elif out['#data_summary']['x1_unit']=='deg':
                out['#data_summary']['x1_name']='Phase'
            elif out['#data_summary']['x1_unit']=='A':
                out['#data_summary']['x1_name']='Magnitude'
            elif out['#data_summary']['x1_unit']=='V':
                out['#data_summary']['x1_name']='Voltage'
        except:
            out['error']='File cannot be read!'
        return out

    def nk(filename):
        out={}
        out['error']=''
        sep_found=False
        data_marker=False
        out['#data_table']=[]
        out['#data_summary']={
            'x1_name':'wavelength',
            'y1_1_name':'n',
            'y1_2_name':'k',
            'x1_col':0,
            'y1_1_col':1,
            'y1_2_col':2,
            'y1_1_unit':'',
            'y1_2_unit':'',
            'y1_1_prefix':'',
            'y1_2_prefix':'',
            }
        try:
            with open(filename, 'r') as f:
                for line in f:
                    tmp=line.strip()
                    if not sep_found:
                        sep=Help.find_separator(tmp,3,sep_list)
                        if sep==None:
                            out['error']="Can't find proper split!"
                            break
                        sep_found=True
                        a=tmp.split(sep)
                        out['#data_summary']['x1_unit']=a[0][-1:]
                        out['#data_summary']['x1_prefix']=a[0][0:-1]
                        out['#data_summary']['y1_1_name']=a[1]
                        out['#data_summary']['y1_2_name']=a[2]
                        data_marker=True
                        continue
                    if data_marker:
                        out['#data_table'].append(tmp.split(sep))
        except:
            out['error']='File cannot be read!'
        if out["#data_table"]:
            out["#data_table"]=array(out["#data_table"]).astype(float)
        return out

    def yml(filename,tab=' '):
        data_marker=False
        out={}
        out['error']=''
        out['#data_table']=[]
        out['#data_summary']={
            'x1_name':'wavelength',
            'y1_1_name':'n',
            'y1_2_name':'k',
            'x1_col':0,
            'y1_1_col':1,
            'y1_2_col':2,
            'x1_unit':'m',
            'x1_prefix':'μ',
            'y1_1_unit':'',
            'y1_2_unit':'',
            'y1_1_prefix':'',
            'y1_2_prefix':'',
            }
        try:
            with open(filename, 'r') as f:
                for line in f:
                    tmp=line.strip()
                    if tmp.startswith('data:'):
                        data_marker=True
                        continue
                    if tmp.startswith('CONDITIONS:'):
                        data_marker=False
                        continue
                    if data_marker:
                        out['#data_table'].append(tmp.split(tab)) 
            out["#data_table"]=array(out["#data_table"]).astype(float)
            out['#data_summary']['tot_row'],out['#data_summary']['tot_col']=shape(out["#data_table"])
        except:
            out['error']='File cannot be read!'

        return out

    def gwyddion_xyz(filename,sep=ihtm_sep):
        out={}
        out['error']=''
        out['#data_table']=[]
        out['#data_summary']={'x1_name':'Position','y1_name':'Position'}
        out['#data_summary']['x1_col']=0
        out['#data_summary']['y1_col']=1
        try:
            with open(filename, 'r') as f:
                for line in f:
                    tmp=line.strip()
                    if tmp.startswith('#'):
                        tmp=tmp.split(':')
                        if tmp[0]=="# Channel":
                            out['#data_summary']['z1_name']=tmp[1].split()[0].strip()
                            out['#data_summary']['z1_col']=2
                        elif tmp[0]=="# Lateral units":
                            out['#data_summary']['x1_unit']=tmp[1].strip()[-1:]
                            out['#data_summary']['x1_prefix']=tmp[1].strip()[0:-1]
                            out['#data_summary']['y1_unit']=out['#data_summary']['x1_unit']
                            out['#data_summary']['y1_prefix']=out['#data_summary']['x1_prefix']
                        elif tmp[0]=="# Value units":
                            out['#data_summary']['z1_unit']=tmp[1].strip()[-1:]
                            out['#data_summary']['z1_prefix']=tmp[1].strip()[0:-1]
                    else:
                        out['#data_table'].append(tmp.split(sep))
            out["#data_table"]=array(out["#data_table"]).astype(float)
            out['#data_summary']['tot_row'],out['#data_summary']['tot_col']=shape(out["#data_table"])
        except:
            out['error']='File cannot be read!'

        return out

    def gwyddion_ascii_matrix(filename,sep=ihtm_sep):
        out={}
        out['error']=''
        out['#data_table']=[]
        out['#data_summary']={'x1_name':'Position','y1_name':'Position'}
        out['#data_summary']['x1_col']='None'
        out['#data_summary']['y1_col']='None'
        try:
            with open(filename, 'r') as f:
                for line in f:
                    tmp=line.strip()
                    if tmp.startswith('#'):
                        tmp=tmp.split(':')
                        if tmp[0]=="# Channel":
                            out['#data_summary']['z1_name']=tmp[1].split()[0].strip()
                            out['#data_summary']['z1_col']='#data_table'
                        elif tmp[0]=="# Value units":
                            out['#data_summary']['z1_unit']=tmp[1].strip()[-1:]
                            out['#data_summary']['z1_prefix']=tmp[1].strip()[0:-1]
                        elif tmp[0]=="# Width":
                            a=tmp[1].split()
                            out['#data_summary']['x1_value']=float(a[0].strip())
                            out['#data_summary']['x1_unit']=a[1].strip()[-1:]
                            out['#data_summary']['x1_prefix']=a[1].strip()[0:-1]
                        elif tmp[0]=="# Height":
                            a=tmp[1].split()
                            out['#data_summary']['y1_value']=float(a[0].strip())
                            out['#data_summary']['y1_unit']=a[1].strip()[-1:]
                            out['#data_summary']['y1_prefix']=a[1].strip()[0:-1]
                    else:
                        out['#data_table'].append(tmp.split(sep))
            out["#data_table"]=array(out["#data_table"]).astype(float)
            out['#data_summary']['tot_row'],out['#data_summary']['tot_col']=shape(out["#data_table"])
        except:
            out['error']='File cannot be read!'
        return out

    def dta(filename):
        out={}
        out['error']=''
        out['#data_table']=[]
        out['#data_summary']={}
        out['#setup']={}
        table_marker=0
        try:
            with open(filename, 'r') as f:
                for line in f:
                    tmp=line.strip().split()
                    if tmp:
                        if tmp[0]=='DATE':
                            temp=tmp[2].split('/')
                            out['#setup'][tmp[3]]=temp[2]+'.'+temp[0]+'.'+temp[1]
                        if tmp[0]=='TIME':
                            out['#setup'][tmp[3]]=tmp[2]
                        if tmp[0]=='PSTAT':
                            out['#setup'][tmp[3]]=tmp[2]
                        if tmp[0]=='SCANRATE':
                            out['#setup']['Scanrate']=tmp[2]
                            out['#setup']['Scanrate_unit']=tmp[5]
                        if tmp[0]=='STEPSIZE':
                            out['#setup']['Stepsize']=tmp[2]
                            out['#setup']['Stepsize_unit']=tmp[5]
                        if tmp[0]=='AREA':
                            out['#setup']['Device_area']=tmp[2]
                            out['#setup']['Device_area_unit']=tmp[5]
                        if tmp[0]=="Pt":
                            out['#data_summary']['x1_name']=tmp[2]
                            out['#data_summary']['x1_col']=2
                            out['#data_summary']['y1_name']=tmp[3]
                            out['#data_summary']['y1_col']=3
                        if tmp[0]=="#":
                            out['#data_summary']['x1_unit']=tmp[2]
                            out['#data_summary']['y1_unit']=tmp[5]
                            table_marker=1
                            continue
                        if table_marker:
                            out['#data_table'].append(tmp)
            out['#data_table']=array(out["#data_table"])
            out['#data_table']=out['#data_table'][:,out['#data_summary']['x1_col']:out['#data_summary']['y1_col']+1]
            out['#data_summary']['x1_col']=0
            out['#data_summary']['y1_col']=1
            out['#data_summary']['x1_prefix']=''
            out['#data_summary']['y1_prefix']=''
            out['#data_summary']['tot_row'],out['#data_summary']['tot_col']=shape(out["#data_table"])
        except:
            out['error']='File cannot be read!'
        return out

    def tmm_proj(filename, split=ihtm_kword_sep, sep=ihtm_sep):
        out={}
        out['error']=""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    tmp=line.strip()
                    a=tmp.split(split)
                    if a[0].startswith("Layer_"):
                        out[a[0]]=a[-1].split(sep)
                    else:
                        out[a[0]]=a[-1]
        except:
            out['error']='File cannot be read!'
        out["Layer_thickness"]=[float(item) for item in out["Layer_thickness"]]
        out['Input_angle']=float(out['Input_angle'])
        out['Simulation_step']=float(out['Simulation_step'])
        return out

    def ini(file, extension='ini', split=ihtm_kword_sep, kwords=ihtm_keywords):
        file=file.replace("."+file.split(".")[-1],"."+extension)
        out={}
        out['error']=''
        try:
            with open(file, 'r') as f:
                for line in f:
                    line=line.strip()
                    tmp=line.split(split)
                    for kword in kwords:
                        if tmp[0] == kword:
                            out[kword]=tmp[-1]
        except:
            out['error']='File cannot be read!'
        return out

    def inst(file, extension='inst', split=ihtm_kword_sep, kwords=instr_keywords):
        file=file.replace("."+file.split(".")[-1],"."+extension)
        out={}
        out['error']=''
        try:
            with open(file, 'r') as f:
                for line in f:
                    line=line.strip()
                    if line.startswith('no_'):
                        tmp=line.split(split)
                        out[tmp[0]]=int(tmp[-1])
                    elif '#device' in line:
                        kword=line
                        out[kword]={}
                    else:
                        tmp=line.split(split)
                        if tmp[0]=='port':
                            tmp[-1]=int(tmp[-1])
                        out[kword][tmp[0]]=tmp[-1]
        except:
            out['error']='File cannot be read!'
        return out

    def dsp(filename):
        out={}
        counter=1
        info_marker=0
        x_data_tmp=[]
        y_data_tmp=[]
        data_marker=0
        out["#data_summary"]={}
        out["#data_summary"]['x1_name']='wavelength'
        out["#data_summary"]['x1_col']=0
        out['error']=''
        try:
            with open(filename,'r') as f:
                for line in f:
                    tmp=line.strip()
                    if counter==4:#info about sample:
                        out['#data_summary']['y1_label']=tmp[0:-4]
                    if counter==10:#on  10 row you get info about measurement
                        info_marker=0
                        out["#data_summary"]['y1_name']=tmp
                        out["#data_summary"]['y1_col']=1
                        if tmp.startswith('%'):
                            out["#data_summary"]['y1_unit']=''
                            out["#data_summary"]['y1_prefix']='c'
                    if info_marker:
                        x_data_tmp.append(float(tmp));
                    if tmp=='nm':#after units you get info about measurement setup
                        out["#data_summary"]['x1_unit']=tmp[-1:]
                        out["#data_summary"]['x1_prefix']=tmp[0:-1]
                        info_marker=1
                    if data_marker:
                        y_data_tmp.append(float(tmp))
                    if tmp=='#DATA':
                        data_marker=1
                    counter+=1
            x_data=linspace(x_data_tmp[0],x_data_tmp[1],int(x_data_tmp[3]))
            y_data=array(y_data_tmp)
            out['#data_table']=swapaxes(array([x_data,y_data]),0,1)#find transpose
            if out["#data_summary"]['y1_name']=='%R':
                out["#data_summary"]['y1_name']='Reflectance'
            elif out["#data_summary"]['y1_name']=='%T':
                out["#data_summary"]['y1_name']='Transmittance'
            elif out["#data_summary"]['y1_name']=='A':
                out["#data_summary"]['y1_name']='Absorbance'
            out['#data_summary']['tot_row'],out['#data_summary']['tot_col']=shape(out["#data_table"])
        except:
            out['error']='File cannot be read!'
        return out

    def ihtm(filename,filetype=None,split=ihtm_kword_sep,sep=ihtm_sep):
        out={}
        out['error']=''
        try:
            with open(filename,'r') as f:
                for line in f:
                    tmp=line.strip()
                    if tmp in ihtm_sections:
                        kword=tmp
                        if kword == "#data_header":
                            out[kword]=[]
                        elif kword=="#data_table":
                            out[kword]=[]
                        else:
                            out[kword]={}
                    else:
                        if kword == "#data_header":
                            out[kword].append(tmp.split(sep))
                        elif kword=="#data_table":
                            out[kword].append(tmp.split(sep))
                        else:
                            a=tmp.split(split)
                            if '_list' in a[0]:
                                out[kword][a[0]]=a[1].split(sep)
                            else:
                                out[kword][a[0]]=a[1]
        except:
            out['error']='File cannot be read!'
        if "#data_table" in out:
            out["#data_table"]=array(out["#data_table"]).astype(float)
        #this is for the old files
        if "#data_header" in out:
            out['#data_summary']={}
            out['#data_summary']['x1_name']=out['#data_header'][0][0]
            out['#data_summary']['x1_unit']=out['#data_header'][1][0][-1:]
            out['#data_summary']['x1_prefix']=out['#data_header'][1][0][0:-1]
            out['#data_summary']['x1_col']=0
            while len(out['#data_header'][0])!=len(out['#data_header'][1]):
                out['#data_header'][1].append('')#if quantity was unitless previously
            if len(out['#data_header'][0])>2:
                for i in range(len(out['#data_header'][0])-1):
                    out['#data_summary'][f'y1_{i+1}_name']=out['#data_header'][0][i+1]
                    out['#data_summary'][f'y1_{i+1}_unit']=out['#data_header'][1][i+1][-1:]
                    out['#data_summary'][f'y1_{i+1}_prefix']=out['#data_header'][1][i+1][0:-1]
                    out['#data_summary'][f'y1_{i+1}_col']=i+1
                    out['#data_summary'][f'y1_{i+1}_label']=path.basename(filename)[0:-5]+f'y1_{i+1}'
            elif len(out['#data_header'][0])==2:
                i=0
                out['#data_summary']['y1_name']=out['#data_header'][0][i+1]
                out['#data_summary']['y1_unit']=out['#data_header'][1][i+1][-1:]
                out['#data_summary']['y1_prefix']=out['#data_header'][1][i+1][0:-1]
                if out['#data_summary']['y1_unit']=='%':
                    out['#data_summary']['y1_unit']=''
                    out['#data_summary']['y1_prefix']='c'
                out['#data_summary']['y1_col']=i+1
                out['#data_summary']['y1_label']=path.basename(filename)[0:-5]
            out.pop("#data_header")
            out['#data_summary']['tot_row'],out['#data_summary']['tot_col']=shape(out["#data_table"])
        #convert to integers
        for key in out['#data_summary'].keys():
            if ('col' in key) or ('row' in key) or ('point' in key):
                out['#data_summary'][key]=int(out['#data_summary'][key])
        poplist=[]
        #clearing out empty keywords
        for kword in out:
            if kword!="#data_table" and kword!='error':
                if not bool(out[kword]):
                    poplist.append(kword)
        for kword in poplist:
            out.pop(kword)
        return out

class Help():
    #mask example ['x1','y1','x2','y2'] or ['x1','y1_1','y1_2']
    def generate_data_dict(mask,quantities,units,prefixes=[],labels=None):
        out={}
        out['symbol_list']=mask
        for idx,item in enumerate(mask):
            out[f'{item}_name']=quantities[idx]
            out[f'{item}_unit']=units[idx]
            out[f'{item}_col']=idx
            if prefixes==[]:
                out[f'{item}_prefix']=''
            if labels!=None:
                out[f'{item}_label']=labels[idx]
        return out

    def find_separator(string_to_be_separated,exprected_col_no,sep_list):
        for item in sep_list:
            if exprected_col_no==len(string_to_be_separated.split(item)):
                return item
        return None
#data is type [[],[]]
    def adjust_string_length(data):
        new_data=[[str(ele) for ele in row] for row in data]
        cmax=[[len(ele) for ele in row] for row in new_data]
        cmax=[max(ele) for ele in zip(*cmax)]
        for rows in new_data:
            for idx in range(0,len(rows)):
                rows[idx]=rows[idx].ljust(cmax[idx])
        return new_data
    
class Write_to():
    #for writing ini or any other files related to the app (current extensions ini or inst)
    #input text should be a dictionary, file is __file__
    def ini_inst_proj(file,text_dict,extension="ini"):
        flag=False
        if 'error' in text_dict:
            tmperror=text_dict.pop('error')
            flag=True
        file=file.replace("."+file.split(".")[-1],"."+extension)
        with open(file,'w') as f:
            for keyword in text_dict:
                if keyword.startswith('#'):
                    savetxt(f, [keyword], delimiter='\t', newline='\n', fmt='%s')
                    for kword in text_dict[keyword]:
                        savetxt(f, [kword+ihtm_kword_sep+str(text_dict[keyword][kword])], delimiter='\t', newline='\n', fmt='%s')
                elif ("Layer_" in keyword) or ("_list" in keyword):
                    tmp=[str(item) for item in text_dict[keyword]]
                    savetxt(f, [keyword+ihtm_kword_sep+ihtm_sep.join(tmp)], delimiter='\t', newline='\n', fmt='%s')
                else:
                    savetxt(f, [keyword+ihtm_kword_sep+str(text_dict[keyword])], delimiter='\t', newline='\n', fmt='%s')
        if flag:
            text_dict['error']=tmperror

    #you pack everything into dictionary, normal filename
    def data(filename,text_dict,fmtlist=None):
        flag=False
        if 'error' in text_dict:
            tmperror=text_dict.pop('error')
            flag=True
        if fmtlist==None:
            fmtlist=[]
            for i in range(0,shape(text_dict['#data_table'])[1]):
                fmtlist.append('%.6e')
        with open(filename,'w') as f:
            for keyword in text_dict:
                savetxt(f, [keyword], delimiter='\t', newline='\n', fmt='%s')
                if keyword=="#data_table":
                    for line in text_dict[keyword]:
                        savetxt(f, [line], delimiter='\t', newline='\n', fmt=fmtlist)
                else:
                    for keywrd in text_dict[keyword]:
                        if '_list' in keywrd:
                            tmp=[str(item) for item in text_dict[keyword][keywrd]]
                            savetxt(f, [keywrd+ihtm_kword_sep+ihtm_sep.join(tmp)], delimiter='\t', newline='\n', fmt='%s')
                        else:
                            savetxt(f, [keywrd+ihtm_kword_sep+str(text_dict[keyword][keywrd])], delimiter='\t', newline='\n', fmt='%s')
        if flag:
            text_dict['error']=tmperror

#old stuff
class Files_RW():
    hashtags=['#comment','#setup','#data_header','#data_table']
    split=':='
    class container():
        pass

#ini stuff
    def check_E60_ini(self,dirname,filename,split):
        out=self.container()
        with open(path.join(dirname,filename), 'r') as f:
            for line in f:
                a=line.strip()
                tmp=a.split(split)
                if tmp[0]=='load_file_path':
                    out.filedir=tmp[-1]
                if tmp[0]=='save_file_path':
                    out.savedir=tmp[-1]
                if tmp[0]=='reference_path':
                    out.refdir=tmp[-1]
                if tmp[0]=='reference_file':
                    out.reffile=tmp[-1]
        return out

    def check_IV_measure_ini(self,dirname,filename,split):
        out=self.container()
        with open(path.join(dirname,filename), 'r') as f:
            for line in f:
                a=line.strip()
                tmp=a.split(split)
                if tmp[0]=='save_file_path':
                    out.savedir=tmp[-1]
        return out

    def check_IV_measure_inst_file(self,dirname,filename,split):
        ip_list=[]
        port_list=[]
        with open(path.join(dirname,filename), 'r') as f:
            for line in f:
                a=line.strip()
                tmp=a.split(split)
                if tmp[0]=="ip_address":
                    ip_list.append(tmp[-1])
                if tmp[0]=="port":
                    port_list.append(int(tmp[-1]))
        return ip_list,port_list

    def check_IV_analysis_ini(self,dirname,filename,split):
        out=self.container()
        with open(path.join(dirname,filename), 'r') as f:
            for line in f:
                a=line.strip()
                tmp=a.split(split)
                if tmp[0]=='load_file_path':
                    out.filedir=tmp[-1]
                if tmp[0]=='database_path':
                    out.dbdir=tmp[-1]
                if tmp[0]=='database_file':
                    out.dbname=tmp[-1]
        return out


#write to files
    def write_to_file(self,dirname,filename,write):
        with open(path.join(dirname,filename),'w') as f:
            for line in write:
                savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')

    def write_header_data(self,dirname,filename,header,data,fmtlist):
        with open(path.join(dirname,filename),'w') as f:
            for line in header:
                savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
            for line in data:
                savetxt(f, [line], delimiter='\t', newline='\n', fmt=fmtlist)

#E60 raw data

    def load_dsp(self,filename):
        out=self.container()
        setup_marker=0
        counter=1
        setup=[]
        data_marker=0
        out.data=[]
        out.data_units=''
        out.error=''
        try:
            with open(filename,'r') as f:
                for line in f:
                    tmp=line.strip()
                    if counter==10:#on  10 row you get info about measurement
                        setup_marker=0
                        if tmp.startswith('%'):
                            out.data_units='%'
                        out.type=tmp
                    if setup_marker:
                        setup.append(float(tmp));
                    if tmp=='nm':#after units you get info about measurement setup
                        setup.append(tmp)
                        setup_marker=1
                    if data_marker:
                        out.data.append(float(tmp))
                    if tmp=='#DATA':
                        data_marker=1
                    counter+=1
        except:
            out.error='File cannot be read!'
        #to be further improved
        out.wlength=linspace(setup[1],setup[2],int(setup[4]))
        out.wlength_units=setup[0]
        out.data=array(out.data)
        if out.type=='%R':
            out.type='Reflectance'
        elif out.type=='%T':
            out.type='Transmittance'
        elif out.type=='A':
            out.type='Absorbance'
        return out
#help functions
    def process_2col_data(self,data,idx):
        col1=data[:,idx[0]]
        col2=data[:,idx[1]]
        return col1,col2

    def reset_markers(self,markers,mykey):
        for key in markers.keys():
            if key==mykey:
                markers[key]=1;
            else:
                markers[key]=0

    #this function is obsolete
    def insert_symbol(self,string_list,symbol):
        #new_string=''
        #for item in string_list:
        #    new_string=new_string+item+symbol
        #new_string=new_string[0:-1]
        new_string=symbol.join(string_list)
        return new_string

    #to have it here although not used
    def Add_items(self,text,itemlist,sep):
        for item in itemlist:
            text=text+str(item)+sep
        return text[:-1]

#my TMM
    def process_TMM_header(self,header,*args):
        if args:
            args=args
        else:
            args=['wavelength','Input media']
        error=''
        wlength_units=''
        data_units=''

        idx=[header[0].index(arg) for arg in args]
        wlength_units=header[1][idx[0]]
        try:
            data_units=header[1][idx[1]]
        except:
            pass
        return idx,wlength_units,data_units,error

    def load_reference_TMM(self,filename):
        out=self.container()
        error=''
        (comment,setup,header,data,error)=self.read_ihtm_file(filename,tab='\t')
        if not error:
            idx,out.wlength_units,out.data_units,erorr=self.process_TMM_header(header)
        if not error:
            out.wlength,out.data=self.process_2col_data(data,idx)
        out.type='Reflectance'
        out.error=error
        return out

#my processed E60
    def process_dtsp_header(self, header):
        error=''
        wlength_units=''
        data_units=''
        idx=[0,1]
        data_type=header[0][idx[1]]
        wlength_units=header[1][idx[0]]
        try:
            data_units=header[1][idx[1]]
        except:
            pass
        return idx,wlength_units,data_units,data_type,error


    def load_dtsp(self,filename):
        out=self.container()
        error=''
        (comment,setup,header,data,error)=self.read_ihtm_file(filename,tab='\t')
        if not error:
            idx,out.wlength_units,out.data_units,out.type,erorr=self.process_dtsp_header(header)
        if not error:
            out.wlength,out.data=self.process_2col_data(data,idx)
        out.error=error
        return out

#measured IV files
    def process_iv_setup(self,setup,*args):
        measurement_date=''
        measurement_time=''
        sample_name=''
        device_area=''
        area_units=''
        if args:
            split=args[0]
        else:
            split=Files_RW.split
        for item in setup:
            tmp=item.split(split)
            if tmp[0]=='measurement_date':
                measurement_date=tmp[-1].replace('.','')
            elif tmp[0]=='measurement_time':
                measurement_time=tmp[-1]
            elif tmp[0]=='sample_name':
                sample_name=tmp[-1]
            elif tmp[0]=='device_area':
                device_area=float(tmp[-1])
            elif tmp[0]=='area_units':
                area_units=tmp[-1]
        return (measurement_date,measurement_time,sample_name,device_area,area_units)

    def process_iv_header(self,header,i,*v):
        idx=self.container()
        idx.i_col=header[0].index(i)
        idx.v_col=[]
        for item in v:
            idx.v_col.append(header[0].index(item))
        v_units=header[1][idx.v_col[-1]]
        i_units=header[1][idx.i_col]
        return (idx, v_units, i_units)

    def process_iv_data(self,table,idx):
        data=array(table)
        v=data[:,idx.v_col[0]].astype(float)
        for i in range(1,len(idx.v_col)):
            v+=data[:,idx.v_col[i]].astype(float)
        i=data[:,idx.i_col].astype(float)
        return (v,i)

    def load_iv_file(self,filename):
        out=self.container()
        out.data=self.container()#measured data
        out.meas=self.container()#data about measurement
        out.cell=self.container()#data about the cell
        out.error=''
        (comment,setup,header,data,error)=self.read_ihtm_file(filename,tab='\t')
        if error=='':
            (idx,out.data.v_units,out.data.i_units)=self.process_iv_header(header,'current','voltage')
            v,i=self.process_iv_data(data,idx)
            out.data.v,out.data.i=v,-i
            (out.meas.date,out.meas.time,sample_name,out.cell.area,out.cell.area_units)=self.process_iv_setup(setup)
            if not out.cell.area_units:
                #so that nothing changes when you don't have exact area
                out.cell.area = 1
                out.cell.area_units = 'cm^2'
            #(out.cell.area,out.cell.area_units)=Analyze_IV().convert_area_units(area,area_units)
            #this is only temporary fix
            #(i,i_units)=Analyze_IV().convert_current_mA(out.data.i,out.data.i_units)
            #out.data.cd=i/out.cell.area#area should be read from your file fix it
            #out.data.cd_units=i_units+'/'+out.cell.area_units#current density
        else:
            out.error=error
        #if table_row!=len(out.data.v):
        #    out.error='Data file is corrupter.'
        return out
#for all of my files
    def read_ihtm_file(self,filename,tab=None):#this should be the same for all files you are creating either in measurements of after processing except for AFM files
        comment=[]
        setup=[]
        header=[]
        data=[]
        error='Wrong type of file!'
        markers={item:0 for item in Files_RW.hashtags}
        try:
            with open(filename, 'r') as f:
                for line in f:
                    tmp=line.strip()

                    if tmp==Files_RW.hashtags[0]:
                        self.reset_markers(markers,tmp)
                        continue
                    elif tmp==Files_RW.hashtags[1]:
                        self.reset_markers(markers,tmp)
                        continue
                    elif tmp==Files_RW.hashtags[2]:
                        self.reset_markers(markers,tmp)
                        continue
                    elif tmp==Files_RW.hashtags[3]:
                        self.reset_markers(markers,tmp)
                        continue

                    if markers[Files_RW.hashtags[0]]:
                        comment.append(tmp)
                    elif markers[Files_RW.hashtags[1]]:
                        setup.append(tmp)
                    elif markers[Files_RW.hashtags[3]]:
                        data.append(tmp.split(tab))
                    elif markers[Files_RW.hashtags[2]]:
                        header.append(tmp.split(tab))
        except:
            error='File cannot be read!'
        if header or comment or setup or data:
            error=''
        return comment, setup, header, array(data).astype(float), error

    #setup should be header
    def load_ascii_matrix(self,filename):
        out=self.container()
        out.setup=[]
        out.data=[]
        out.error='Wrong type of file!'
        try:
            with open(filename, 'r') as f:
                for line in f:
                    tmp=line.strip()
                    if tmp.startswith('#'):
                        out.setup.append(tmp)
                    else:
                        out.data.append(tmp.split('\t'))
        except:
            out.error='File cannot be read!'

        if out.setup:
            out.x,out.x_units,out.y,out.y_units,out.z_name,out.z_units=self.process_ascii_matrix_setup(out.setup)
        if out.data:
            try:
                out.data=array(out.data).astype(float)
                out.error=''
            except:
                pass
        return out

    def process_ascii_matrix_setup(self, setup):
        for line in setup:
            tmp=line.split(':')
            if tmp[0] =='# Channel':
                z_name=tmp[-1].split('(')[0].strip()
            elif tmp[0]=='# Width':
                [x,x_units]=tmp[-1].strip().split(' ')
            elif tmp[0]=='# Height':
                [y,y_units]=tmp[-1].strip().split(' ')
            elif tmp[0]=='# Value units':
                z_units=tmp[-1].strip()
        return float(x),x_units,float(y),y_units,z_name,z_units
#dta file from prof. Dragisa
    def load_dta_file(self,filename):
        out=self.container()
        out.data=self.container()
        out.meas=self.container()
        out.cell=self.container()
        out.error=''
        (comment,header,data,error)=self.read_dta_file(filename)
        if error=='':
            (idx,out.data.v_units,out.data.i_units)=self.process_iv_header(header,'Im','Vf','Vu')
            v,i=self.process_iv_data(data,idx)
            out.data.v,out.data.i=-v,-i
            (out.meas.date,out.meas.time,area,area_units,table_row)=self.process_dta_comment(comment)
            #area is always in cm^2
            #(out.cell.area,out.cell.area_units)=Analyze_IV().convert_area_units(area,area_units)
            #current density should be in mA/cm^2
            #(i,i_units)=Analyze_IV().convert_current_mA(out.data.i,out.data.i_units)
            #out.data.cd=i/out.cell.area
            #out.data.cd_units=i_units+'/'+out.cell.area_units#current density
        else:
            out.error=error
        if table_row!=len(out.data.v):
            out.error='Data file is corrupter.'
        return out

    def read_dta_file(self,filename):
        comment=[]
        data=[]
        header=[]
        error=''
        comment_marker=1#comment text at beginning that is why this is set to negative
        header_marker=0#set to positive so it wait when table header starts
        table_marker=0#set to positive to wait when table starts
        try:
            with open(filename,'r') as f:
                for line in f:
                    if comment_marker:
                        comment.append(line.strip())
                    #header of table
                    if header_marker:
                        header.append(line.strip().split('\t'))#because of units we need to split
                    #table itself
                    if table_marker:
                        data.append(line.strip().split('\t'))#because of qunatities we need to split
                    #marker changes
                    tmp=line.strip().split('\t')
                    if tmp[0]=='CURVE':
                        comment_marker=0
                        header_marker=1
                    if tmp[0]=='#':
                        header_marker=0
                        table_marker=1
        except:
            error='File cannot be read.'
        return (comment,header,data,error)

    def process_dta_comment(self,comment):
        for line in comment:
            tmp=line.split('\t')
            if tmp[0]=='DATE':
                american_date=tmp[2].split('/')
                measurement_date=self.insert_symbol([american_date[2],american_date[0],american_date[1]],'')
            if tmp[0]=='TIME':
                measurement_time=tmp[2]
            if tmp[0]=='AREA':
                device_area=float(tmp[2])
                area_units=tmp[3].split()[-1][1:-1]
            if tmp[0]=='CURVE':
                table_row=int(tmp[2])
        return (measurement_date,measurement_time,device_area,area_units,table_row)
