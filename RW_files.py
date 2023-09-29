#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 18 16:19:18 2022

@author: tzework
"""
import numpy as np
import os

#for loading a file you need first read function that reads it
#then you need process functions that are processing it
#they are called from loading function that is saying all is okay and gives data back to main script





class Files_RW():
    hashtags=['#comment','#setup','#data_header','#data_table']
              
    class container():
        pass
    
    #to have it here although not used
    def Add_items(self,text,itemlist,sep):
        for item in itemlist:
            text=text+str(item)+sep
        return text[:-1]

    def check_E60_ini(self,dirname,filename,split):
        out=self.container()
        with open(os.path.join(dirname,filename), 'r') as f:
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
        with open(os.path.join(dirname,filename), 'r') as f:
            for line in f:
                a=line.strip()
                tmp=a.split(split)
                if tmp[0]=='save_file_path':
                    out.savedir=tmp[-1]
        return out

    def check_IV_measure_inst_file(self,dirname,filename,split):
        ip_list=[]
        with open(os.path.join(dirname,filename), 'r') as f:
            for line in f:
                a=line.strip()
                tmp=a.split(split)
                ip_list.append(tmp[-1])
        return ip_list

    def write_to_file(self,dirname,filename,write):
        with open(os.path.join(dirname,filename),'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')

    def write_header_data(self,dirname,filename,header,data,fmtlist):
        with open(os.path.join(dirname,filename),'w') as f:
            for line in header:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
            for line in data:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt=fmtlist)

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
        #to be furthered improved
        out.wlength=np.linspace(setup[1],setup[2],int(setup[4]))
        out.wlength_units=setup[0]
        out.data=np.array(out.data)
        if out.type=='%R':
            out.type='Reflectance'
        elif out.type=='%T':
            out.type='Transmittance'
        elif out.type=='A':
            out.type='Absorbance'
        return out

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

    def process_2col_data(self,data,idx):
        col1=data[:,idx[0]]
        col2=data[:,idx[1]]
        return col1,col2

    def load_reference_TMM(self,filename,*args,**kwargs):
        out=self.container()
        error=''
        (comment,setup,header,data,error)=self.read_ihtm_file(filename,**kwargs)
        if not error:
            idx,out.wlength_units,out.data_units,erorr=self.process_TMM_header(header)
        if not error:
            out.wlength,out.data=self.process_2col_data(data,idx)
        out.type='Reflectance'
        out.error=error
        return out


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


    def load_dtsp(self,filename,*args,**kwargs):
        out=self.container()
        error=''
        (comment,setup,header,data,error)=self.read_ihtm_file(filename,**kwargs)
        if not error:
            idx,out.wlength_units,out.data_units,out.type,erorr=self.process_dtsp_header(header)
        if not error:
            out.wlength,out.data=self.process_2col_data(data,idx)
        out.error=error
        return out

    def reset_markers(self,markers,mykey):
        for key in markers.keys():
            if key==mykey:
                markers[key]=1;
            else:
                markers[key]=0

    def read_ihtm_file(self,filename,**kwargs):#this should be the same for all files you are creating either in measurements of after processing except for AFM files
        comment=[]
        setup=[]
        header=[]
        data=[]
        error='Wrong type of file!'
        if kwargs:
            markers={value:0 for value in kwargs.values()}
        else:
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
                        data.append(tmp.split('\t'))
                    elif markers[Files_RW.hashtags[2]]:
                        header.append(tmp.split('\t'))
        except:
            error='File cannot be read!'
        if header or comment or setup or data:
            error=''
        return comment, setup, header, np.array(data).astype('float'), error 