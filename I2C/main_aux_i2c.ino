#include "Config.h"
#include <Wire.h>
#include <DFRobot_SHT20.h>
#include <ArduinoLowPower.h>
#include <FlashStorage_SAMD.h>
#include <QuickMedianLib.h>
#include <MKRWAN.h>

#define opto1 9
#define opto2 10
#define opto3 0
#define mux2 8
#define mux1 7
#define mux0 6
#define SLAVE_ADDRESS 0x6b

uint8_t number2[24];
int values[7];
const int NUM_DOUBLES_ALPHA = 3; 
const int NUM_DOUBLES_BETA = 3; 
const int TOTAL_DOUBLES = NUM_DOUBLES_ALPHA + NUM_DOUBLES_BETA + 1; 
float valores_a_mandar[6];
int sleep_permiso = 0;

DFRobot_SHT20 sht20;
LoRaModem lora;

int i,j=0;
void setup() {
  // put your setup code here, to run once:
  pinMode (opto1, OUTPUT);
  pinMode (opto2, OUTPUT);
  pinMode (opto3, OUTPUT);
  pinMode (mux0, OUTPUT);
  pinMode (mux1, OUTPUT);
  pinMode (mux2, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
}

void receiveData(int byteCount) {
  double receivedData[TOTAL_DOUBLES];
  byte buffer[sizeof(double) * TOTAL_DOUBLES];
  
  int index = 0;
  while (Wire.available() && index < sizeof(buffer)) {
    buffer[index++] = Wire.read();
  }

  if (index == sizeof(buffer)) {
    for (int i = 0; i < TOTAL_DOUBLES; i++) {
      memcpy(&receivedData[i], &buffer[i * sizeof(double)], sizeof(double));
    }

    Serial.println("Alpha list:");
    for (int i = 0; i < NUM_DOUBLES_ALPHA; i++) {
      Serial.print("Received double: ");
      Serial.println(receivedData[i], 8);
    }

    Serial.println("Beta list:");
    for (int i = NUM_DOUBLES_ALPHA; i < NUM_DOUBLES_ALPHA + NUM_DOUBLES_BETA; i++) {
      Serial.print("Received double: ");
      Serial.println(receivedData[i], 8);
    }

    Serial.println("Check value:");
    Serial.print("Received double: ");
    Serial.println(receivedData[NUM_DOUBLES_ALPHA + NUM_DOUBLES_BETA], 8);

    sleep_permiso = 1;
    
  } else {
    Serial.println("Error: Received data size mismatch");
  }
}

void sendData() {
  Serial.println("Ejecuto sendData():");
  Serial.println(valores_a_mandar[3]);
  int values[7];
  values[0] = (int)valores_a_mandar[0]; //Sensor 0
  values[1] = (int)valores_a_mandar[1]; //Sensor 1
  values[2] = (int)valores_a_mandar[2]; //Sensor 2
  values[3] = (int)valores_a_mandar[3]; //Sensor 3
  values[4] = (int)valores_a_mandar[4]; //Sensor 4
  values[5] = (int)valores_a_mandar[5]; //Sensor 5
  values[6] = 23456;
  uint8_t number[14];

  for (int i = 0; i < 7; i++) {
    int highByte = (values[i] >> 8) & 0xFF;
    int lowByte = values[i] & 0xFF;
    number[i * 2] = highByte;
    number[i * 2 + 1] = lowByte;
  }

  Serial.print("Sending values: ");
  for (int i = 0; i < 7; i++) {
    Serial.print(values[i]);
    if (i < 7) {
      Serial.print(", ");
    }
  }
  Serial.println();

  Wire.write(number, sizeof(number));
}

int measure_battery(){

  int Vmin = 3700;
  int Vmax = 5300;
  int median_value=0;
  for(int i =0;i<nSamples;i++){
    median_value=median_value+analogRead(A1);
  }
  median_value=median_value/nSamples;
  int battery=map(median_value, 0, 1023, 0, 6600);
    
  if (battery>Vmax){
    battery=Vmax;
  }
  else if (battery<=Vmin){
    battery=Vmin;
  }
  int batt=map(battery, Vmin, Vmax, 1, 100);
  Serial.print ("Porcentaje de bateria: ");
  Serial.println (batt); 
  
  return batt; 
}

void operate_optos(int value){
  digitalWrite(opto1,value);
  digitalWrite(opto2,value);
  digitalWrite(opto3,value);
  delay(1000);
}

void loop() {
  sleep_permiso = 0;
  float medianValues[8]={0,0,0,0,0,0,0,0};
  Wire.begin();
  //digitalWrite(LED_BUILTIN,LOW);
  int nDiscards[8]={0,0,0,0,0,0,0,0};
  float Hr[8],Hra[8],HfK[8],HfKa[8],L[8]={0,0,0,0,0,0,0,0};
  float dcM[4]={0,0,0,0};
  float c,battery=0;
  int a,b,addr=0;
  
  int writeMemo[16][2]={{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0},{0,0}};
  uint8_t payload[34]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  float airH[10],airT[10]={0,0,0,0,0,0,0,0,0,0};
  float adcReadings[6][10]={{0,0,0,0,0,0,0,0,0,0},
                            {0,0,0,0,0,0,0,0,0,0},
                            {0,0,0,0,0,0,0,0,0,0},
                            {0,0,0,0,0,0,0,0,0,0},
                            {0,0,0,0,0,0,0,0,0,0},
                            {0,0,0,0,0,0,0,0,0,0}};

  float humedad;
  //Setting up I2C
  LoRaModem *lora = new LoRaModem();
  Serial.begin(9600);
  delay(100);

  //Turn on optos
  operate_optos(1);
  delay(100);
  Serial.println("Optos turn on: OK");
  //Setting up SHT20
  sht20.initSHT20();
  delay(100);
  sht20.checkSHT20();
  delay(100);
  
  Serial.println("Setting up variables: OK");

  //Reading SHT20 values
  for (i = 0; i < nSamples; i++) {
    airH[i] = sht20.readHumidity();
    if (airH[i] > sht20_humidity_higherLimit || airH[i] < sht20_humidity_lowerLimit) {
      nDiscards[0] = nDiscards[0] + 1;
    }
    airT[i] = sht20.readTemperature();
    if (airT[i] > sht20_temperature_higherLimit || airH[i] < sht20_temperature_lowerLimit) {
      nDiscards[1] = nDiscards[1] + 1;
    }
  }
  Serial.println("Reading SHT20 values: OK");
  //Reading adc sensors
  for (i=0;i<numberADCSensorsConnected;i++) {
    digitalWrite(mux0, valores[i][0]);
    digitalWrite(mux1, valores[i][1]);
    digitalWrite(mux2, valores[i][2]);
    Serial.print("i: ");
    Serial.println(i);
    for (j=0;j<nSamples;j++) {
      //adcReadings[i][j] = ads.readADC_SingleEnded(0);
      adcReadings[i][j] = analogRead(A0);
      if (adcReadings[i][j] > soilwatch_higherLimit || adcReadings[i][j] < soilwatch_lowerLimit) {
        nDiscards[i+2] = nDiscards[i+2]+1;
        Serial.print("nDiscards: ");
        Serial.println(nDiscards[i+2]);
      }
    }
  }
  digitalWrite(mux0, LOW);
  digitalWrite(mux1, LOW);
  digitalWrite(mux2, LOW);
  for(i=0;i<8;i++){
    Serial.println(nDiscards[i]);
  }
  Serial.println("Reading ADC values: OK");
  delay(100);
  battery=measure_battery();
  delay(100);
  Wire.end();
  //Turn off optos
  operate_optos(0);

  delay(100);
  //Calculate medians
  medianValues[0] = QuickMedian<float>::GetMedian(airH, nSamples);
  medianValues[1] = QuickMedian<float>::GetMedian(airT, nSamples);
  for (i=0;i<numberADCSensorsConnected;i++) {
    medianValues[i+2] = QuickMedian<float>::GetMedian(adcReadings[i], nSamples);
    valores_a_mandar[i] = medianValues[i+2];
    Serial.println(medianValues[i+2]);
  }
  Serial.println("Medidas aire");
  Serial.println(medianValues[0]);
  if(medianValues[0]>100){medianValues[0]=100;}
  else if(medianValues[0]<0){medianValues[0]=0;}
  Serial.println(medianValues[1]);
    if(medianValues[1]>125){medianValues[1]=125;}
  else if(medianValues[1]<-40){medianValues[1]=-40;}
  delay(100);
  Serial.println("Median values calculated: OK");
  //Calibrate ADC values
  uint8_t var[8]={0,0,0,0,0,0,0,0};
  for (i=0;i<numberADCSensorsConnected;i++) {
    medianValues[i+2] = pow((medianValues[i+2]*(3.3/1023.0)),2)*0.056359-0.0011769*(medianValues[i+2]*(3.3/1023.0))-0.0045260;
    
    if(medianValues[i+2]<0){
      medianValues[i+2] = 0.0;
    }
    var[i+2]=round(245*medianValues[i+2]+5);
    //Serial.println(medianValues[i+2]);
    var[0]=round((49.0/20.0)*medianValues[0]+5);
    Serial.println("medianValues[1]");
    Serial.println(medianValues[1]);
    var[1]=round(49.0*medianValues[1]+2125)/33;
    Serial.println(var[1]);
  }
  Serial.println("Calibrate ADC values: OK");
 //Filter data
  for (i=0;i<sizeof(nDiscards)/sizeof(nDiscards[0]);i++) {
    if (nDiscards[i]>=10){
      Hr[i]=0;
    }
    else {
      Hr[i]=medianValues[i];
    }
    if(Hr[i]<0){Hr[i]=0;}
    //Serial.println(medianValues[i],4);
    Serial.println(Hr[i],4);
  }
    addr = 0;
    a,b=0;
    Serial.println("Hra");
    for(int i=0;i<sizeof(Hra)/sizeof(Hra[0]);i++){
      a=EEPROM.read(addr);
      if(a==255){a=0;}
      b=EEPROM.read(addr+1);
      if(b==255){b=0;}
      //Serial.println(a);
      //Serial.println(b);
      if(i==0){
        Hra[i]=a+b*0.01;
      }
      else if(i==1){
        Hra[i]=(((a+b*0.01)*11-680)/17);
        if(Hra[i]==-40){Hra[i]=0;}
      }
      else{
        Hra[i]=(a+b*0.01)*0.01;
      }
      addr=addr+2;
      Serial.println(Hra[i],4);
    }
    Serial.println("L");
    for (i=0;i<sizeof(nDiscards)/sizeof(nDiscards[0]);i++) {
      if (Hr[i]==0){
        L[i]=0;
        //Serial.println("L es 0");
      }
      else if(Hra[i]==0){
        L[i]=1;
       // Serial.println("L es 1");
      }
      else{
        L[i]=0.9;
        //Serial.println("L es 0.9");
      }
      Serial.println(L[i]);
    }
    addr = 16;
    Serial.println("HfKa");
    for (i=0;i< sizeof(medianValues)/sizeof(medianValues[0]);i++) {
      a=EEPROM.read(addr);
      if(a==255){
        a=0;
      }
      b=EEPROM.read(addr+1);
      if(b==255){
        b=0;
      }
      //Serial.println(i);
      //Serial.println(a);
      //Serial.println(b);
      if(i==0){
        HfKa[i]=a+b*0.01;
      }
      else if(i==1) {
        HfKa[i]=(((a+b*0.01)*11-680)/17);
        if(HfKa[i]==-40){HfKa[i]=0;}
      }
      else{
        HfKa[i]=(a+b*0.01)*0.01;
        //Serial.println("suelo");
      }
      addr = addr + 2;
      Serial.println(HfKa[i],4);
    }
    Serial.println("HfK");
     for (i=0;i<sizeof(medianValues)/sizeof(medianValues[0]);i++) {
    if (Hr[i]!= 0) {
        HfK[i]=L[i]*Hr[i]+(1-L[i])*HfKa[i];
      }
      else {
        HfK[i]=0;
      }
      Serial.println(HfK[i],4);
    }
    int cont[2]={0,0};
    for(i=2;i<sizeof(medianValues)/sizeof(medianValues[0]);i++) {
      if(i<5 && HfK[i]!=0) {
        cont[0] = cont[0] + 1;
      }
      else if(i>=5 && HfK[i]!=0){
        cont[1]=cont[1]+1;
      }
    }
    dcM[0] = HfK[0];
    dcM[1] = HfK[1];
    if(cont[0]!=0){dcM[2] = (HfK[2] + HfK[3] + HfK[4]) / cont[0];}
    else{dcM[2]=0;}
    if(cont[0]!=0){dcM[3] = (HfK[5] + HfK[6] + HfK[7]) / cont[1];}
    else{dcM[3]=0;}
    Serial.println("dcM");
    for(i=0;i<4;i++){
      Serial.println(dcM[i],4);
    }
    Serial.println("Memoria");
    //Write in memory
    for(i=0;i<sizeof(medianValues)/sizeof(medianValues[0]);i++){
      if(i==0){
        writeMemo[i][0]=Hr[i];
        writeMemo[i][1]=(Hr[i]-writeMemo[i][0])*100;
        writeMemo[i+8][0]=HfK[i];
        writeMemo[i+8][1]=(HfK[i]-writeMemo[i+8][0])*100;
      }
      else if(i==1){
        c=(17*Hr[i]+680)/11;
        writeMemo[i][0]=c;
        writeMemo[i][1]=(c-writeMemo[i][0])*100;
        c=(17*HfK[i]+680)/11;
        writeMemo[i+8][0]=c;
        writeMemo[i+8][1]=(c-writeMemo[i+8][0])*100;
      }
      else{
        writeMemo[i][0]=Hr[i]*100;
        writeMemo[i][1]=(Hr[i]*100-writeMemo[i][0])*100;
        writeMemo[i+8][0]=HfK[i]*100;
        writeMemo[i+8][1]=(HfK[i]*100-writeMemo[i+8][0])*100;
      }
    }
    Serial.println("writeMemo");
    for(i=0;i<sizeof(writeMemo)/sizeof(writeMemo[0]);i++){
      Serial.print(writeMemo[i][0]);
      Serial.print(" ");
      Serial.println(writeMemo[i][1]);
    }
    addr=0;
    for(i=0;i<16;i++){
      EEPROM.update(addr,writeMemo[i][0]);
      EEPROM.update(addr+1,writeMemo[i][1]);
      EEPROM.commit();
      addr=addr+2;
    }

    Serial.println("Payloads");
       
    payload[0]=3; //Numero de capas
    payload[1]=battery; //Bateria
    payload[2]=245*((dcM[2]+dcM[3])/2.0)+5; //Humedad media tierra
    //payload[2]=608.99826*((dcM[2]+dcM[3])/2)+17.10688541;
    payload[3]=0; //Capa0
    payload[4]=round((49.0/20.0)*Hr[0]+5);//*(49.0/20)+5; Humedad raw aire
    payload[5]=round((49.0/20.0)*HfK[0]+5);//*(49.0/20)+5;//HfK[0]; Humedad filtrada aire
    payload[6]=nDiscards[0]; 
    payload[7]=round((49.0*Hr[1]+2125)/33.0);//*49+2125)/33;//Hr[1]*(49/33)-(6125/33)+250;// Temperatura raw aire
    payload[8]=round((49.0*HfK[1]+2125)/33.0);//*49+2125)/33; Temperatura filtrada aire
    payload[9]=nDiscards[1];
    payload[10]=1; //Capa1
    payload[11]=round(245*Hr[2]+5); //Humedad raw suelo sensor 1 capa 1
    //payload[11]=608.99826*Hr[2]+17.10688541;
    payload[12]=round(245*HfK[2]+5);//Humedad filtrada suelo sensor 1 capa 1
    payload[13]=nDiscards[2];
    payload[14]=round(245*Hr[3]+5); //Humedad raw suelo sensor 2 capa 1
    payload[15]=round(245*HfK[3]+5); //Humedad filtrada suelo sensor 2 capa 1
    payload[16]=nDiscards[3];
    payload[17]=round(245*Hr[4]+5); //Humedad raw suelo sensor 3 capa 1
    payload[18]=round(245*HfK[4]+5); //Humedad filtrada suelo sensor 3 capa 1
    payload[19]=nDiscards[4];
    payload[20]=round(245*dcM[2]+5);//(payload[12]+payload[15]+payload[18])/3;//
    payload[21]=2; //Capa2
    payload[22]=round(245*Hr[5]+5); //Humedad raw suelo sensor 1 capa 2
    payload[23]=round(245*HfK[5]+5); //Humedad filtrada suelo sensor 1 capa 2
    payload[24]=nDiscards[5];
    payload[25]=round(245*Hr[6]+5); //Humedad raw suelo sensor 2 capa 2
    payload[26]=round(245*HfK[6]+5); //Humedad filtrada suelo sensor 2 capa 2
    payload[27]=nDiscards[6];
    payload[28]=round(245*Hr[7]+5); //Humedad raw suelo sensor 3 capa 2
    payload[29]=round(245*HfK[7]+5); //Humedad filtrada suelo sensor 3 capa 2
    payload[30]=nDiscards[7];
    payload[31]=round(245*dcM[3]+5);//(payload[23]+payload[26]+payload[29])/3;//
    payload[32]=0; //N1
    payload[33]=0; //N2

    //uint8_t payload[34]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    int i;
    for (i=2;i<=31;i++){
        if (i==3 || i==6 || i==9 || i==10 || i==13 || i==16 || i==19 || i==21 || i==24 || i==27 || i==30) {
            continue; // saltar la iteración actual del bucle si j está en la lista
        }
        else{
            if(payload[i]<5){payload[i]=5;}
            else if(payload[i]>250){payload[i]=250;}           
        }
    }
    if (!lora->begin(EU868)) {
    Serial.println("Error al inicializar el modulo");
 };
  Serial.print("Version de tu modulo: ");
  Serial.println(lora->version());
  Serial.print("Tu device EUI es: ");
  Serial.println(lora->deviceEUI());

  int connected = lora->joinOTAA(appEui, appKey);
  if (!connected) {
    Serial.println("Ocurrio un error en la conexion a TTN");
  };
   //lora.restart();
   lora->beginPacket();
   //Serial.println("Calculo");
   //Serial.println(sizeof(payload));
   //Serial.println(sizeof(payload[0]));
   lora->write(payload,sizeof(payload));
   Serial.println("Payload sent OK");
   int err = lora->endPacket(true);
   if (err > 0) {
    Serial.println("Message sent correctly!");
   } else {
    Serial.println("Error sending message :(");
    Serial.println("(you may send a limited amount of messages per minute, depending on the signal strength");
    Serial.println("it may vary from 1 message every couple of seconds to 1 message every minute)");
    }
   digitalWrite(LED_BUILTIN,LOW);
   Serial.end();
   delete lora;
   Serial.println("Antes de abrir el Wire:");
   Serial.println(medianValues[3]);
   // LowPower.deepSleep(1*1000);
   Wire.begin(SLAVE_ADDRESS);
   while (sleep_permiso == 0) {
        delay(1000);
   }
   Wire.end();
   delay(1*1000);
}
