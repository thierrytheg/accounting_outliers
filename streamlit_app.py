import altair as alt
import pandas as pd
import streamlit as st
import base64
import os
import matplotlib.pyplot as plt
import numpy as np

def download_link_csv(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'



uploaded_file = st.file_uploader("Choose a file")

try:
    if uploaded_file is not None:
        try:
            df=pd.read_excel(uploaded_file)

        except:
            try:
                df=pd.read_csv(uploaded_file)

            except:
                pass

    else:
        df=pd.read_csv('sample_data.csv')
        st.error("You are currently viewing a sample dataset. Upload your own file to view your data.")
except:
    pass

#Detect column with Account Listing

#sensitivity=st.write("**Sensitivity**")

add_slidebar1= st.slider('Sensitivity', 0, 100, 50,help='Drag the slider to the right to increase the sensitivity which will result in more outliers detected. Drag to the slider to the left to decrease the sensitivity and reduce the number of outliers. ')


try:

    for n in range(len(df.columns)):
        if ('acc' or 'account') in (df.columns[n]).lower():
            df['Account']=df[df.columns[n]]

            add_selectbox = st.selectbox(
            "Select an account from the list below",
            sorted(list(df.Account.unique())))   
 
    #Detect column with dollar values
    for n in range(len(df.columns)):
        if ('am' or 'amount') in (df.columns[n]).lower():
            df['Amount']=df[df.columns[n]]
    
 
    new_columns=['Account','Amount']
    for column in new_columns:
        if column in df.columns:
            pass
        else:
            st.write("Unable to detect your %s column. Please rename the appropriate column '%s' and re-upload the file" %(column,column))
except:
    pass
     

#df['Abs_Val']=abs(df['Amount'].astype(float))

##filter out all rows with values under 1
#df=df.loc[df['Abs_Val']>1]
 
##convert First_Digit column to string and extract first digit
#df['First_Digit']=(df['Abs_Val']).apply(str).str[0]
 
##create series with count for each first digit
#benford_df=df['First_Digit'].value_counts()
#benford_df['Your_Dist_Pct']=round((benford_df/benford_df.sum())*100,1)
 
##create a temporary dataframe to plot Benford Distribution
#benford_list=(benford_df['Your_Dist_Pct']).to_list()



#data={
#'First_Digit':[1,2,3,4,5,6,7,8,9],
#'Your_Distribution' : benford_list,
#'Benford_Distribution': [30.1,17.6,12.5,9.7,7.9,6.7,5.8,5.1,4.6]
#}



#st.write(df[df['First_Digit'].isin([1,2,3,4,5,6,7,8,9])])

#df_plot=pd.DataFrame(data=data,columns=['First_Digit','Your_Distribution','Benford_Distribution'])

 

 
#labels = df_plot['First_Digit']

#Benford_Distribution = list(df_plot['Benford_Distribution'])
#Your_Distribution = list(df_plot['Your_Distribution'])
 
#x = np.arange(len(labels))
#width = 0.35
 
#fig, ax = plt.subplots()
 
#rects1 = ax.bar(x - width/2, Benford_Distribution, width, label='Benford_Distribution')
#rects2 = ax.bar(x + width/2, Your_Distribution, width, label='Your_Distribution')
 

#ax.set_xlabel('First Digit')
#ax.set_ylabel('Distribution')
 
#ax.set_title("Your Data Distribution vs Benford's Distribution")
#ax.set_xticks(x)
#ax.set_xticklabels(labels)
#ax.legend()
 
 
#def autolabel(rects):

#    for rect in rects:
#        height = rect.get_height()
#        ax.annotate(''.format(height),
#                    xy=(rect.get_x() + rect.get_width() / 2, height),
#                    xytext=(0, 3),
#                    textcoords="offset points",
#                    ha='center', va='bottom')
 
 
#autolabel(rects1)
#autolabel(rects2)
 
#fig.tight_layout()
 
q1_sensitivity=add_slidebar1/100
q3_sensitivity=1-q1_sensitivity

def render(account):
  selected=df[df.Account==account]
 
  outlierq3=(selected[selected.columns].loc[selected['Amount']>(np.quantile(selected['Amount'],q3_sensitivity))])
  outlierq1=(selected[selected.columns].loc[selected['Amount']<(np.quantile(selected['Amount'],q1_sensitivity))])
 


  quant=[]
  quant.append([abs(np.quantile(selected['Amount'],q3_sensitivity)),abs(np.quantile(selected['Amount'],q1_sensitivity))])

  if (len(outlierq1) and len(outlierq3)) == 0:
    st.write("No outliers were detected for this account")

  else:

    df_final=pd.concat([outlierq1,outlierq3])
    df_final=df_final.drop_duplicates()

    st.write("Outliers Detected: **%s**" %df_final.shape[0])
  
    st.write(df_final)
   
    tmp_download_link_csv = download_link_csv(df_final, 'your_outliers.csv', 'Download you file here.')
    st.markdown(tmp_download_link_csv, unsafe_allow_html=True)

    return alt.Chart(selected).mark_boxplot().encode(y='Amount',).properties(width=300,height=500).configure_boxplot(extent=1-(add_slidebar1/100))


try:    

    st.altair_chart(render(add_selectbox),use_container_width=True)

except Exception as e:
    pass
#st.pyplot(fig)
