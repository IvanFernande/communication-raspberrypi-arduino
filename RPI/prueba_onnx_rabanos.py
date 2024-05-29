import numpy as np
import requests
import pandas as pd
from datetime import datetime, timedelta
import onnxruntime as ort
from sklearn import preprocessing


dia1 = datetime.now() - timedelta(days=1)
dia1_str = str(dia1)
dia1_dia = dia1_str[:10]

dia2 = dia1 - timedelta(days=2)
dia2_str = str(dia2)
dia2_dia = dia2_str[:10]

dia1_dia="2024-04-24"
dia2_dia="2024-04-20"

# API call

url = f'http://93.93.118.40/rest/measurement-ground-rest/get-calibrated-data-node?name=ifernandez&password=Ivan2002&device_id=650acb3d209aa728fc5e0432&startDatetime={dia2_dia}&endDatetime={dia1_dia}'

response = requests.get(url)

if response.status_code == 200:
    data_api = response.json()
    
    # API to DataFrame
    Sensor0 = []
    Sensor1 = []
    Sensor2 = []
    Sensor3 = []
    Sensor4 = []
    Sensor5 = []

    DateTime = []

    data = data_api.get('data')

    for j in range(len(data)):
        DateTime_aux = data[j].get('timestamp')
        DateTime_aux = DateTime_aux[:19]
        DateTime.append(DateTime_aux)
        Sensor0.append(data[j].get('Humedad calibrada capa 1 sensor 1'))
        Sensor1.append(data[j].get('Humedad calibrada capa 1 sensor 2'))
        Sensor2.append(data[j].get('Humedad calibrada capa 1 sensor 3'))
        Sensor3.append(data[j].get('Humedad calibrada capa 2 sensor 1'))
        Sensor4.append(data[j].get('Humedad calibrada capa 2 sensor 2'))
        Sensor5.append(data[j].get('Humedad calibrada capa 2 sensor 3'))
        
    df = pd.DataFrame({
        'Sensor 0': Sensor0,
        'Sensor 1': Sensor1,
        'Sensor 2': Sensor2,
        'Sensor 3': Sensor3,
        'Sensor 4': Sensor4,
        'Sensor 5': Sensor5
    }, index=pd.to_datetime(DateTime))

    df["Capa 1"] = df.iloc[:, 0:2].mean(axis=1)
    df["Capa 2"] = df.iloc[:, 2:4].mean(axis=1)
    df["Capa 3"] = df.iloc[:, 4:].mean(axis=1)

    #Sampling

    col_names=["Sensor 0", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5"]
    first_hour = df.index.min()
    first_hour = str(first_hour)
    new_index = pd.date_range(first_hour, df.index.max(), freq='15T')

    df_new = pd.DataFrame(index=new_index,columns=col_names)

    df_concat = pd.concat([df, df_new])
    df_concat = df_concat.sort_index()

    df_interpolated = df_concat.interpolate(method="cubic")

    import autosat
    index_sat = autosat.analyze_moisture_data(df_interpolated['Capa 1'])


    new_index2 = pd.date_range(index_sat, df.index.max(), freq='15T')

    df_new2 = pd.DataFrame(index=new_index2,columns=col_names)

    df_concat2 = pd.concat([df_interpolated, df_new2])
    df_concat2 = df_concat2.sort_index()

    df_concat3 = df_concat2[~df_concat2.index.duplicated(keep='last')]

    df_interpolated2 = df_concat3.interpolate(method="cubic")

    df_sampled = df_interpolated2.loc[pd.date_range(index_sat, df.index.max(), freq='15T')]
    df_sampled = df_sampled.iloc[:48]
    
    onnx_model_path = "model_seq_sat_48_fl.onnx"
    session = ort.InferenceSession(onnx_model_path)

    ls_sensor = ["Capa 1","Capa 2","Capa 3"]
    x=np.array(df_sampled[ls_sensor], dtype=np.float32)
    x=np.transpose(x).reshape((1,3,48)).astype(np.float32)    
    x = x.reshape((1,3,48,1))
    
    input_name = session.get_inputs()[0].name
    y = session.run(None, {input_name: x})[0]
 
    fc = 0.25
    sat = 0.493
    
    alpha = np.zeros(3)
    beta = np.zeros(3)
    for l in range(3):
        vwc_sat_sensor = x[0,l,0,0]
        vwc_cc_sensor = y[0,l,]
        vwc_sat_true = sat
        vwc_cc_true = fc

        A = np.array([[vwc_sat_sensor,1],[vwc_cc_sensor,1]])
        A  = np.float64(A)
        B = np.array([[vwc_sat_true],[vwc_cc_true]], dtype=np.float64)
        C=np.matmul(np.linalg.inv(A),B)
        beta[l] = C[1]
        alpha[l]= C[0] 
    print("Alpha:",alpha," Beta:",beta)
    
else:
    print("Alpha:",[1, 1, 1]," Beta:",[0, 0, 0])

