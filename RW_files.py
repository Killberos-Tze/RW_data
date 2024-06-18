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
    split=':='
              
    class container():
        pass
    

#ini files
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
    
    def check_IV_analysis_ini(self,dirname,filename,split):
        out=self.container()
        with open(os.path.join(dirname,filename), 'r') as f:
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
        with open(os.path.join(dirname,filename),'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')

    def write_header_data(self,dirname,filename,header,data,fmtlist):
        with open(os.path.join(dirname,filename),'w') as f:
            for line in header:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
            for line in data:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt=fmtlist)

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
        data=np.array(table)
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
            
        return comment, setup, header, np.array(data).astype(float), error

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
                out.data=np.array(out.data).astype(float)
                out.error=''
            except:
                pass
        return out

    def process_ascii_matrix_setup(self, setup):
        for line in setup:
            tmp=line.split(':')
            if tmp[0] =='# Channel':
                z_name=tmp[-1].strip().split(' ')[0]
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

    
