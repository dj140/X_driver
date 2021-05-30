EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 3 6
Title "Motor Driver"
Date "2021-03-25"
Rev "1.0.0"
Comp "Dj140"
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text HLabel 6750 2450 2    50   Input ~ 0
SPI_nCS
Text HLabel 6750 2550 2    50   Input ~ 0
SPI_SCK
Text HLabel 6750 2650 2    50   Input ~ 0
SPI_MOSI
Text HLabel 6750 2750 2    50   Output ~ 0
SPI_MISO
Wire Wire Line
	5350 2450 6750 2450
Wire Wire Line
	6750 2550 5350 2550
Wire Wire Line
	5350 2650 6750 2650
Wire Wire Line
	6750 2750 5350 2750
Text HLabel 8500 2950 2    50   Output ~ 0
nFAULT
Text HLabel 8500 3050 2    50   Output ~ 0
nOCTW
Wire Wire Line
	6250 800  5900 800 
Wire Wire Line
	5900 1150 5350 1150
$Comp
L power:GND #PWR?
U 1 1 5E39257E
P 6250 1000
AR Path="/5E2D92F4/5E39257E" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/5E39257E" Ref="#PWR046"  Part="1" 
F 0 "#PWR046" H 6250 750 50  0001 C CNN
F 1 "GND" H 6255 827 50  0000 C CNN
F 2 "" H 6250 1000 50  0001 C CNN
F 3 "" H 6250 1000 50  0001 C CNN
	1    6250 1000
	1    0    0    -1  
$EndComp
Text Label 6050 800  0    50   ~ 0
GVDD
Wire Wire Line
	6850 800  6600 800 
Wire Wire Line
	6600 1250 5350 1250
Text Label 6650 800  0    50   ~ 0
AVDD
Wire Wire Line
	7300 800  7100 800 
Wire Wire Line
	7100 1350 5350 1350
$Comp
L power:GND #PWR?
U 1 1 5E396A43
P 7300 1000
AR Path="/5E2D92F4/5E396A43" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/5E396A43" Ref="#PWR051"  Part="1" 
F 0 "#PWR051" H 7300 750 50  0001 C CNN
F 1 "GND" H 7305 827 50  0000 C CNN
F 2 "" H 7300 1000 50  0001 C CNN
F 3 "" H 7300 1000 50  0001 C CNN
	1    7300 1000
	1    0    0    -1  
$EndComp
Text Label 7100 800  0    50   ~ 0
DVDD
Wire Wire Line
	5350 1650 7650 1650
Wire Wire Line
	7800 1400 7650 1400
Wire Wire Line
	7650 1400 7650 1650
Wire Wire Line
	7800 1750 5350 1750
Wire Wire Line
	5350 1850 7650 1850
Wire Wire Line
	7650 1850 7650 2100
Wire Wire Line
	7650 2100 7800 2100
Wire Wire Line
	8500 1400 8000 1400
Wire Wire Line
	8500 1750 8000 1750
Wire Wire Line
	8500 2100 8000 2100
Text Label 8500 1400 0    50   ~ 0
SH_A
Text Label 8500 1750 0    50   ~ 0
SH_B
Text Label 8500 2100 0    50   ~ 0
SH_C
Wire Wire Line
	5350 2050 5750 2050
Wire Wire Line
	5950 2050 5950 2150
Wire Wire Line
	5950 2150 5350 2150
Wire Wire Line
	6750 2350 5350 2350
Connection ~ 7800 2400
Wire Wire Line
	7800 2400 8000 2400
Wire Wire Line
	7200 3050 7200 3250
Wire Wire Line
	7200 3250 5350 3250
Wire Wire Line
	7200 3050 8000 3050
Wire Wire Line
	7100 3150 7100 2950
Wire Wire Line
	7100 2950 7800 2950
Wire Wire Line
	5350 3150 7100 3150
Wire Wire Line
	7800 2700 7800 2950
Connection ~ 7800 2950
Wire Wire Line
	8000 2700 8000 3050
Connection ~ 8000 3050
Wire Wire Line
	8000 3050 8500 3050
$Comp
L power:GND #PWR?
U 1 1 5E3DEDE4
P 5350 4950
AR Path="/5E2D92F4/5E3DEDE4" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/5E3DEDE4" Ref="#PWR044"  Part="1" 
F 0 "#PWR044" H 5350 4700 50  0001 C CNN
F 1 "GND" H 5355 4777 50  0000 C CNN
F 2 "" H 5350 4950 50  0001 C CNN
F 3 "" H 5350 4950 50  0001 C CNN
	1    5350 4950
	1    0    0    -1  
$EndComp
Text Notes 6950 5550 0    50   ~ 0
with careful placement a single GND plane \nis better than spliting the GND into analog\nand digital. providing better lowest \nimpedence path for each current loop.
Wire Wire Line
	3500 2350 3500 2300
Wire Wire Line
	3550 2350 3500 2350
Text HLabel 2300 1200 0    50   Input ~ 0
EN_GATE
$Comp
L power:GND #PWR?
U 1 1 605E5EBD
P 2450 1500
AR Path="/5E2D92F4/605E5EBD" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/605E5EBD" Ref="#PWR036"  Part="1" 
F 0 "#PWR036" H 2450 1250 50  0001 C CNN
F 1 "GND" H 2455 1327 50  0000 C CNN
F 2 "" H 2450 1500 50  0001 C CNN
F 3 "" H 2450 1500 50  0001 C CNN
	1    2450 1500
	1    0    0    -1  
$EndComp
Wire Wire Line
	2300 1200 2450 1200
Wire Wire Line
	3300 2550 3550 2550
Wire Wire Line
	2650 2200 3100 2200
Wire Wire Line
	3100 2200 3100 2850
Wire Wire Line
	3100 2850 3550 2850
$Comp
L power:GND #PWR?
U 1 1 5E41691B
P 2250 2200
AR Path="/5E2D92F4/5E41691B" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/5E41691B" Ref="#PWR035"  Part="1" 
F 0 "#PWR035" H 2250 1950 50  0001 C CNN
F 1 "GND" H 2255 2027 50  0000 C CNN
F 2 "" H 2250 2200 50  0001 C CNN
F 3 "" H 2250 2200 50  0001 C CNN
	1    2250 2200
	1    0    0    -1  
$EndComp
Wire Wire Line
	2350 2200 2250 2200
Text HLabel 2600 3350 0    50   Input ~ 0
PWM_BH
Text HLabel 2600 3050 0    50   Input ~ 0
PWM_BL
Text HLabel 2600 3450 0    50   Input ~ 0
PWM_CH
Text HLabel 2600 3150 0    50   Input ~ 0
PWM_CL
Text HLabel 2600 3250 0    50   Input ~ 0
PWM_AH
Text HLabel 2600 2950 0    50   Input ~ 0
PWM_AL
Wire Wire Line
	2600 2950 3550 2950
Wire Wire Line
	3550 3050 2600 3050
Wire Wire Line
	2600 3150 3550 3150
Wire Wire Line
	3550 3250 2600 3250
Wire Wire Line
	3550 3350 2600 3350
Wire Wire Line
	2600 3450 3550 3450
Wire Wire Line
	5900 800  5900 1150
Wire Wire Line
	6600 800  6600 1250
Wire Wire Line
	7100 800  7100 1350
Wire Wire Line
	2450 1200 3300 1200
Wire Wire Line
	3300 1200 3300 2550
Connection ~ 2450 1200
Text Label 5800 3550 0    50   ~ 0
GH_A
Text Label 5800 3650 0    50   ~ 0
GH_B
Text Label 5800 3750 0    50   ~ 0
GH_C
Text Label 5800 3850 0    50   ~ 0
GL_A
Text Label 5800 3950 0    50   ~ 0
GL_B
Text Label 5800 4050 0    50   ~ 0
GL_C
Wire Wire Line
	5350 3550 5800 3550
Wire Wire Line
	5800 3650 5350 3650
Wire Wire Line
	5350 3750 5800 3750
Wire Wire Line
	5800 3850 5350 3850
Wire Wire Line
	5350 3950 5800 3950
Wire Wire Line
	5800 4050 5350 4050
Text Label 2850 3550 0    50   ~ 0
SH_A
Text Label 2850 3650 0    50   ~ 0
SH_B
Text Label 2850 3750 0    50   ~ 0
SH_C
Text Label 2850 3850 0    50   ~ 0
SL_A
Text Label 2850 3950 0    50   ~ 0
SL_B
Text Label 2850 4050 0    50   ~ 0
SL_C
Wire Wire Line
	2850 3550 3550 3550
Wire Wire Line
	2850 3650 3550 3650
Wire Wire Line
	3550 3750 2850 3750
Wire Wire Line
	2850 3850 3550 3850
Wire Wire Line
	3250 4150 3550 4150
Wire Wire Line
	3250 4250 3550 4250
Wire Wire Line
	3250 4350 3550 4350
Wire Wire Line
	3250 4450 3550 4450
Text Label 3250 4150 0    50   ~ 0
SP1
Text Label 3250 4250 0    50   ~ 0
SN1
Text Label 3250 4350 0    50   ~ 0
SP2
Text Label 3250 4450 0    50   ~ 0
SN2
Wire Wire Line
	3200 4800 3200 4550
Wire Wire Line
	3200 4550 3550 4550
$Comp
L power:GND #PWR?
U 1 1 605E5EAA
P 3200 5000
AR Path="/5E2D92F4/605E5EAA" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/605E5EAA" Ref="#PWR038"  Part="1" 
F 0 "#PWR038" H 3200 4750 50  0001 C CNN
F 1 "GND" H 3205 4827 50  0000 C CNN
F 2 "" H 3200 5000 50  0001 C CNN
F 3 "" H 3200 5000 50  0001 C CNN
	1    3200 5000
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 605E5EAC
P 3450 5000
AR Path="/5E2D92F4/605E5EAC" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/605E5EAC" Ref="#PWR039"  Part="1" 
F 0 "#PWR039" H 3450 4750 50  0001 C CNN
F 1 "GND" H 3455 4827 50  0000 C CNN
F 2 "" H 3450 5000 50  0001 C CNN
F 3 "" H 3450 5000 50  0001 C CNN
	1    3450 5000
	1    0    0    -1  
$EndComp
Wire Wire Line
	3450 4700 3450 4650
Wire Wire Line
	3450 4650 3550 4650
Wire Wire Line
	6150 4350 5800 4350
Wire Wire Line
	5800 4350 5800 4150
Wire Wire Line
	5800 4150 5350 4150
Wire Wire Line
	5350 4250 5700 4250
Wire Wire Line
	6200 4950 5700 4950
Wire Wire Line
	5700 4250 5700 4950
Wire Wire Line
	6500 4950 6750 4950
Text HLabel 6950 4950 2    50   Output ~ 0
CSENSE_2
Wire Wire Line
	6950 4950 6750 4950
Connection ~ 6750 4950
Text HLabel 6950 4350 2    50   Output ~ 0
CSENSE_1
Wire Wire Line
	6950 4350 6600 4350
Connection ~ 6600 4350
Wire Wire Line
	6600 4350 6450 4350
Wire Wire Line
	9650 2450 9650 2500
Wire Wire Line
	9650 2450 9350 2450
Wire Wire Line
	9350 2450 9350 2600
Connection ~ 9650 2450
Text HLabel 9950 2450 2    50   Output ~ 0
TEMP_SENSE
Wire Wire Line
	9950 2450 9650 2450
Text GLabel 5750 800  0    50   UnSpc ~ 0
GVDD
Wire Wire Line
	5750 800  5900 800 
Connection ~ 5900 800 
Wire Wire Line
	2850 3950 3550 3950
Wire Wire Line
	2850 4050 3550 4050
Wire Wire Line
	2150 5700 2200 5700
Wire Wire Line
	2150 6450 2200 6450
Text Label 1600 5700 0    50   ~ 0
GH_A
Text Label 2975 5700 0    50   ~ 0
GH_B
Text Label 4700 5700 0    50   ~ 0
GH_C
Wire Wire Line
	4700 5700 4900 5700
Wire Wire Line
	2975 5700 3175 5700
Wire Wire Line
	1600 5700 1850 5700
Text Label 1650 6450 0    50   ~ 0
GL_A
Text Label 2965 6440 0    50   ~ 0
GL_B
Text Label 4700 6450 0    50   ~ 0
GL_C
Wire Wire Line
	4700 6450 4900 6450
Wire Wire Line
	1650 6450 1850 6450
$Comp
L power:GND #PWR?
U 1 1 609AF5B4
P 5500 7500
AR Path="/5E2D92F4/609AF5B4" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/609AF5B4" Ref="#PWR045"  Part="1" 
F 0 "#PWR045" H 5500 7250 50  0001 C CNN
F 1 "GND" H 5505 7327 50  0000 C CNN
F 2 "" H 5500 7500 50  0001 C CNN
F 3 "" H 5500 7500 50  0001 C CNN
	1    5500 7500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 609AF5BA
P 4000 7495
AR Path="/5E2D92F4/609AF5BA" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/609AF5BA" Ref="#PWR042"  Part="1" 
F 0 "#PWR042" H 4000 7245 50  0001 C CNN
F 1 "GND" H 4005 7322 50  0000 C CNN
F 2 "" H 4000 7495 50  0001 C CNN
F 3 "" H 4000 7495 50  0001 C CNN
	1    4000 7495
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 609AF5C0
P 2500 6875
AR Path="/5E2D92F4/609AF5C0" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/609AF5C0" Ref="#PWR037"  Part="1" 
F 0 "#PWR037" H 2500 6625 50  0001 C CNN
F 1 "GND" H 2505 6702 50  0000 C CNN
F 2 "" H 2500 6875 50  0001 C CNN
F 3 "" H 2500 6875 50  0001 C CNN
	1    2500 6875
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 7395 4000 7495
Wire Wire Line
	5500 7350 5500 7500
Text Label 2500 6110 0    50   ~ 0
SH_A
Text Label 3800 6090 0    50   ~ 0
SH_B
Text Label 5500 6095 0    50   ~ 0
SH_C
Text Label 2100 6850 0    50   ~ 0
SL_A
Text Label 3450 6845 0    50   ~ 0
SL_B
Text Label 5000 6850 0    50   ~ 0
SL_C
Text Label 2800 7095 0    50   ~ 0
SN1
Text Label 2800 7395 0    50   ~ 0
SP1
Text Label 4450 7050 0    50   ~ 0
SN2
Text Label 4450 7350 0    50   ~ 0
SP2
Wire Wire Line
	3800 7095 4000 7095
Connection ~ 4000 7095
Wire Wire Line
	3800 7395 4000 7395
Connection ~ 4000 7395
Wire Wire Line
	3300 7095 3200 7095
Wire Wire Line
	3200 7095 3200 7145
Wire Wire Line
	2800 7095 3200 7095
Connection ~ 3200 7095
Wire Wire Line
	3600 7395 3200 7395
Wire Wire Line
	3200 7395 3200 7345
Wire Wire Line
	2800 7395 3200 7395
Connection ~ 3200 7395
Connection ~ 5500 7050
Connection ~ 5500 7350
Wire Wire Line
	4900 7300 4900 7350
Wire Wire Line
	4900 7350 5300 7350
Wire Wire Line
	5000 7050 4900 7050
Wire Wire Line
	4900 7050 4900 7100
Wire Wire Line
	4900 7050 4450 7050
Connection ~ 4900 7050
Wire Wire Line
	4450 7350 4900 7350
Connection ~ 4900 7350
Wire Wire Line
	2000 5000 2000 5350
Wire Wire Line
	3450 6845 4000 6845
Wire Wire Line
	4000 6845 4000 7095
Wire Wire Line
	5000 6850 5500 6850
Wire Wire Line
	5500 6850 5500 7050
Wire Wire Line
	2100 6850 2500 6850
Text Notes 750  7250 0    50   ~ 0
FET Gate Charge Total= 41nC.\nGate Driver avg current = 41nC x 6 x sw Freq
Text Notes 7350 6450 0    50   ~ 0
MP30 can handle 30A peak and 15A cont.\nif more current is needed, the connector \ncan be changed.
Wire Wire Line
	2000 5350 2500 5350
Wire Wire Line
	2500 5400 2500 5350
Connection ~ 2500 5350
Wire Wire Line
	2500 5350 2600 5350
Connection ~ 2600 6000
Wire Wire Line
	2600 6000 2500 6000
Connection ~ 2700 6000
Wire Wire Line
	2700 6000 2600 6000
Wire Wire Line
	2800 6000 2700 6000
Wire Wire Line
	2600 5400 2600 5350
Connection ~ 2600 5350
Wire Wire Line
	2600 5350 2700 5350
Wire Wire Line
	2700 5400 2700 5350
Connection ~ 2700 5350
Wire Wire Line
	2700 5350 2800 5350
Wire Wire Line
	2800 5400 2800 5350
Connection ~ 2800 5350
Connection ~ 2800 6000
Wire Wire Line
	2900 6000 2800 6000
Wire Wire Line
	3500 5700 3475 5700
Wire Wire Line
	2800 5350 3800 5350
Wire Wire Line
	2500 6150 2600 6150
Connection ~ 2600 6150
Wire Wire Line
	2600 6150 2700 6150
Connection ~ 2700 6150
Wire Wire Line
	2700 6150 2800 6150
Wire Wire Line
	2500 6150 2500 6040
Connection ~ 2500 6150
Connection ~ 2500 6000
Wire Wire Line
	2500 6750 2500 6850
Wire Wire Line
	2900 6750 2800 6750
Connection ~ 2500 6750
Connection ~ 2600 6750
Wire Wire Line
	2600 6750 2500 6750
Connection ~ 2700 6750
Wire Wire Line
	2700 6750 2600 6750
Connection ~ 2800 6750
Wire Wire Line
	2800 6750 2700 6750
Wire Wire Line
	2500 6875 2500 6850
Connection ~ 2500 6850
Wire Wire Line
	2965 6440 3175 6440
Wire Wire Line
	3500 6440 3475 6440
Wire Wire Line
	3800 5400 3800 5350
Connection ~ 3800 5350
Wire Wire Line
	3800 5350 3900 5350
Wire Wire Line
	3900 5400 3900 5350
Connection ~ 3900 5350
Wire Wire Line
	3900 5350 4000 5350
Wire Wire Line
	4000 5400 4000 5350
Connection ~ 4000 5350
Wire Wire Line
	4000 5350 4100 5350
Wire Wire Line
	4100 5400 4100 5350
Connection ~ 4100 5350
Wire Wire Line
	3800 6000 3900 6000
Connection ~ 3900 6000
Wire Wire Line
	3900 6000 4000 6000
Connection ~ 4000 6000
Wire Wire Line
	4000 6000 4100 6000
Wire Wire Line
	3800 6140 3900 6140
Connection ~ 3900 6140
Wire Wire Line
	3900 6140 4000 6140
Connection ~ 4000 6140
Wire Wire Line
	4000 6140 4100 6140
Wire Wire Line
	3800 6140 3800 6100
Connection ~ 3800 6140
Connection ~ 3800 6000
Wire Wire Line
	4200 6000 4100 6000
Connection ~ 4100 6000
Wire Wire Line
	4200 6740 4100 6740
Connection ~ 3900 6740
Wire Wire Line
	3900 6740 3800 6740
Connection ~ 4000 6740
Wire Wire Line
	4000 6740 3900 6740
Connection ~ 4100 6740
Wire Wire Line
	4100 6740 4000 6740
Wire Wire Line
	4000 6740 4000 6845
Connection ~ 4000 6845
Wire Wire Line
	5500 5400 5500 5350
Connection ~ 5500 5350
Wire Wire Line
	5600 5400 5600 5350
Wire Wire Line
	5500 5350 5600 5350
Connection ~ 5600 5350
Wire Wire Line
	5600 5350 5700 5350
Wire Wire Line
	5700 5400 5700 5350
Connection ~ 5700 5350
Wire Wire Line
	5700 5350 5800 5350
Wire Wire Line
	5800 5400 5800 5350
Wire Wire Line
	5500 6000 5500 6150
Wire Wire Line
	5900 6000 5800 6000
Connection ~ 5500 6000
Connection ~ 5600 6000
Wire Wire Line
	5600 6000 5500 6000
Connection ~ 5700 6000
Wire Wire Line
	5700 6000 5600 6000
Connection ~ 5800 6000
Wire Wire Line
	5800 6000 5700 6000
Wire Wire Line
	5800 6150 5700 6150
Connection ~ 5500 6150
Connection ~ 5600 6150
Wire Wire Line
	5600 6150 5500 6150
Connection ~ 5700 6150
Wire Wire Line
	5700 6150 5600 6150
Wire Wire Line
	5900 6750 5800 6750
Connection ~ 5600 6750
Wire Wire Line
	5600 6750 5500 6750
Connection ~ 5700 6750
Wire Wire Line
	5700 6750 5600 6750
Connection ~ 5800 6750
Wire Wire Line
	5800 6750 5700 6750
Wire Wire Line
	5500 6850 5500 6750
Connection ~ 5500 6850
Connection ~ 5500 6750
Wire Wire Line
	7050 6200 6300 6200
Wire Wire Line
	6300 6200 6300 6150
Wire Wire Line
	6300 6150 5800 6150
Connection ~ 5800 6150
Wire Wire Line
	7050 6100 3800 6100
Connection ~ 3800 6100
Wire Wire Line
	3800 6100 3800 6000
Wire Wire Line
	7050 6000 6175 6000
Wire Wire Line
	6175 6000 6175 6040
Wire Wire Line
	6175 6040 2500 6040
Connection ~ 2500 6040
Wire Wire Line
	2500 6040 2500 6000
$Comp
L power:VDC #PWR?
U 1 1 609AF666
P 2000 5000
AR Path="/5E2D92F4/609AF666" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/609AF666" Ref="#PWR034"  Part="1" 
F 0 "#PWR034" H 2000 4900 50  0001 C CNN
F 1 "VDC" V 2000 5145 50  0000 L CNN
F 2 "" H 2000 5000 50  0001 C CNN
F 3 "" H 2000 5000 50  0001 C CNN
	1    2000 5000
	1    0    0    -1  
$EndComp
Wire Wire Line
	7550 800  7550 1450
$Comp
L power:GND #PWR?
U 1 1 5E3983AF
P 7700 1000
AR Path="/5E2D92F4/5E3983AF" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/5E3983AF" Ref="#PWR052"  Part="1" 
F 0 "#PWR052" H 7700 750 50  0001 C CNN
F 1 "GND" H 7705 827 50  0000 C CNN
F 2 "" H 7700 1000 50  0001 C CNN
F 3 "" H 7700 1000 50  0001 C CNN
	1    7700 1000
	1    0    0    -1  
$EndComp
$Comp
L power:VDC #PWR?
U 1 1 605E5E8A
P 8355 800
AR Path="/5E2D92F4/605E5E8A" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/605E5E8A" Ref="#PWR055"  Part="1" 
F 0 "#PWR055" H 8355 700 50  0001 C CNN
F 1 "VDC" V 8355 1030 50  0000 L CNN
F 2 "" H 8355 800 50  0001 C CNN
F 3 "" H 8355 800 50  0001 C CNN
	1    8355 800 
	0    1    1    0   
$EndComp
Wire Wire Line
	7700 800  7550 800 
Connection ~ 7700 800 
Wire Wire Line
	5350 1450 7550 1450
NoConn ~ 5350 1585
NoConn ~ 5350 1950
NoConn ~ 5350 3350
$Comp
L power:+3.3VA #PWR058
U 1 1 60867A37
P 9650 2050
F 0 "#PWR058" H 9650 1900 50  0001 C CNN
F 1 "+3.3VA" H 9665 2223 50  0000 C CNN
F 2 "" H 9650 2050 50  0001 C CNN
F 3 "" H 9650 2050 50  0001 C CNN
	1    9650 2050
	1    0    0    -1  
$EndComp
$Comp
L power:GNDA #PWR059
U 1 1 6086ECC3
P 9650 2800
F 0 "#PWR059" H 9650 2550 50  0001 C CNN
F 1 "GNDA" H 9655 2627 50  0000 C CNN
F 2 "" H 9650 2800 50  0001 C CNN
F 3 "" H 9650 2800 50  0001 C CNN
	1    9650 2800
	1    0    0    -1  
$EndComp
$Comp
L power:GNDA #PWR057
U 1 1 6086EF5A
P 9350 2800
F 0 "#PWR057" H 9350 2550 50  0001 C CNN
F 1 "GNDA" H 9355 2627 50  0000 C CNN
F 2 "" H 9350 2800 50  0001 C CNN
F 3 "" H 9350 2800 50  0001 C CNN
	1    9350 2800
	1    0    0    -1  
$EndComp
Wire Wire Line
	4100 5350 5500 5350
Wire Wire Line
	7800 2950 8500 2950
$Comp
L power:GND #PWR?
U 1 1 6061965A
P 3550 2650
AR Path="/5E2D92F4/6061965A" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/6061965A" Ref="#PWR041"  Part="1" 
F 0 "#PWR041" H 3550 2400 50  0001 C CNN
F 1 "GND" H 3555 2477 50  0000 C CNN
F 2 "" H 3550 2650 50  0001 C CNN
F 3 "" H 3550 2650 50  0001 C CNN
	1    3550 2650
	0    1    1    0   
$EndComp
$Comp
L power:+3.3VA #PWR040
U 1 1 60619F7E
P 3500 2300
F 0 "#PWR040" H 3500 2150 50  0001 C CNN
F 1 "+3.3VA" H 3515 2473 50  0000 C CNN
F 2 "" H 3500 2300 50  0001 C CNN
F 3 "" H 3500 2300 50  0001 C CNN
	1    3500 2300
	1    0    0    -1  
$EndComp
$Comp
L power:+3.3V #PWR053
U 1 1 6061B59A
P 7800 2400
F 0 "#PWR053" H 7800 2250 50  0001 C CNN
F 1 "+3.3V" H 7815 2573 50  0000 C CNN
F 2 "" H 7800 2400 50  0001 C CNN
F 3 "" H 7800 2400 50  0001 C CNN
	1    7800 2400
	1    0    0    -1  
$EndComp
$Comp
L power:GNDA #PWR043
U 1 1 60622814
P 5350 4850
F 0 "#PWR043" H 5350 4600 50  0001 C CNN
F 1 "GNDA" V 5355 4722 50  0000 R CNN
F 2 "" H 5350 4850 50  0001 C CNN
F 3 "" H 5350 4850 50  0001 C CNN
	1    5350 4850
	0    -1   -1   0   
$EndComp
$Comp
L power:GNDA #PWR050
U 1 1 60623A37
P 6850 1000
F 0 "#PWR050" H 6850 750 50  0001 C CNN
F 1 "GNDA" H 6855 827 50  0000 C CNN
F 2 "" H 6850 1000 50  0001 C CNN
F 3 "" H 6850 1000 50  0001 C CNN
	1    6850 1000
	1    0    0    -1  
$EndComp
$Comp
L power:GNDA #PWR047
U 1 1 60624F7C
P 6600 4550
F 0 "#PWR047" H 6600 4300 50  0001 C CNN
F 1 "GNDA" H 6605 4377 50  0000 C CNN
F 2 "" H 6600 4550 50  0001 C CNN
F 3 "" H 6600 4550 50  0001 C CNN
	1    6600 4550
	1    0    0    -1  
$EndComp
$Comp
L power:GNDA #PWR049
U 1 1 60625C33
P 6750 5150
F 0 "#PWR049" H 6750 4900 50  0001 C CNN
F 1 "GNDA" H 6755 4977 50  0000 C CNN
F 2 "" H 6750 5150 50  0001 C CNN
F 3 "" H 6750 5150 50  0001 C CNN
	1    6750 5150
	1    0    0    -1  
$EndComp
$Comp
L power:+3.3V #PWR048
U 1 1 6062648C
P 6750 2350
F 0 "#PWR048" H 6750 2200 50  0001 C CNN
F 1 "+3.3V" H 6765 2523 50  0000 C CNN
F 2 "" H 6750 2350 50  0001 C CNN
F 3 "" H 6750 2350 50  0001 C CNN
	1    6750 2350
	1    0    0    -1  
$EndComp
NoConn ~ 3550 2750
NoConn ~ 3550 2450
NoConn ~ 5350 2950
NoConn ~ 5350 1515
NoConn ~ 5350 3450
$Comp
L Device:C_Small C?
U 1 1 605E5E81
P 6250 900
AR Path="/5E2D92F4/605E5E81" Ref="C?"  Part="1" 
AR Path="/6062DC24/605E5E81" Ref="C26"  Part="1" 
F 0 "C26" V 6150 750 50  0000 L CNN
F 1 "2.2uF 25V" V 6350 700 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 6250 900 50  0001 C CNN
F 3 "~" H 6250 900 50  0001 C CNN
F 4 "" H 6250 900 50  0001 C CNN "Description"
F 5 "GRM155C81E225KE11D" H 6250 900 50  0001 C CNN "MPN"
F 6 "C12530" H 6250 900 50  0001 C CNN "LCSC Part #"
	1    6250 900 
	1    0    0    -1  
$EndComp
$Comp
L Device:C_Small C?
U 1 1 605E5E83
P 6850 900
AR Path="/5E2D92F4/605E5E83" Ref="C?"  Part="1" 
AR Path="/6062DC24/605E5E83" Ref="C29"  Part="1" 
F 0 "C29" V 6750 750 50  0000 L CNN
F 1 "1uF 25V" V 6950 700 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 6850 900 50  0001 C CNN
F 3 "~" H 6850 900 50  0001 C CNN
F 4 "GMK105CC6105MV-F" H 6850 900 50  0001 C CNN "MPN"
F 5 "C52923" H 6850 900 50  0001 C CNN "LCSC Part #"
	1    6850 900 
	1    0    0    -1  
$EndComp
$Comp
L Device:C_Small C?
U 1 1 5E39DE04
P 7900 2100
AR Path="/5E2D92F4/5E39DE04" Ref="C?"  Part="1" 
AR Path="/6062DC24/5E39DE04" Ref="C34"  Part="1" 
F 0 "C34" V 7850 2200 50  0000 C CNN
F 1 "0.1uF 50V" V 7950 2350 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 7900 2100 50  0001 C CNN
F 3 "~" H 7900 2100 50  0001 C CNN
F 4 "GCM155L8EH104KE07D" H 7900 2100 50  0001 C CNN "MPN"
	1    7900 2100
	0    1    1    0   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 5E3B02BD
P 7900 1750
AR Path="/5E2D92F4/5E3B02BD" Ref="C?"  Part="1" 
AR Path="/6062DC24/5E3B02BD" Ref="C33"  Part="1" 
F 0 "C33" V 7850 1850 50  0000 C CNN
F 1 "0.1uF 50V" V 7950 2000 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 7900 1750 50  0001 C CNN
F 3 "~" H 7900 1750 50  0001 C CNN
F 4 "GCM155L8EH104KE07D" H 7900 1750 50  0001 C CNN "MPN"
	1    7900 1750
	0    1    1    0   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 605E5E99
P 7900 1400
AR Path="/5E2D92F4/605E5E99" Ref="C?"  Part="1" 
AR Path="/6062DC24/605E5E99" Ref="C32"  Part="1" 
F 0 "C32" V 7850 1500 50  0000 C CNN
F 1 "0.1uF 50V" V 7950 1650 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 7900 1400 50  0001 C CNN
F 3 "~" H 7900 1400 50  0001 C CNN
F 4 "GCM155L8EH104KE07D" H 7900 1400 50  0001 C CNN "MPN"
	1    7900 1400
	0    1    1    0   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 5E3B42A0
P 5850 2050
AR Path="/5E2D92F4/5E3B42A0" Ref="C?"  Part="1" 
AR Path="/6062DC24/5E3B42A0" Ref="C25"  Part="1" 
F 0 "C25" V 5900 1900 50  0000 R CNN
F 1 "22nF 50V" V 5800 1900 50  0000 R CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 5850 2050 50  0001 C CNN
F 3 "~" H 5850 2050 50  0001 C CNN
F 4 "C0402C223K5REC7411" H 5850 2050 50  0001 C CNN "MPN"
F 5 "C1532" H 5850 2050 50  0001 C CNN "LCSC Part #"
	1    5850 2050
	0    -1   -1   0   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 5E3B7595
P 7300 900
AR Path="/5E2D92F4/5E3B7595" Ref="C?"  Part="1" 
AR Path="/6062DC24/5E3B7595" Ref="C30"  Part="1" 
F 0 "C30" V 7200 750 50  0000 L CNN
F 1 "1uF 25V" V 7400 700 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 7300 900 50  0001 C CNN
F 3 "~" H 7300 900 50  0001 C CNN
F 4 "GMK105CC6105MV-F" H 7300 900 50  0001 C CNN "MPN"
F 5 "C52923" H 7300 900 50  0001 C CNN "LCSC Part #"
	1    7300 900 
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E3C4147
P 8000 2550
AR Path="/5E2D92F4/5E3C4147" Ref="R?"  Part="1" 
AR Path="/6062DC24/5E3C4147" Ref="R40"  Part="1" 
F 0 "R40" V 7900 2600 50  0000 C CNN
F 1 "10k" V 8000 2550 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 7930 2550 50  0001 C CNN
F 3 "~" H 8000 2550 50  0001 C CNN
F 4 "CRCW040210K0FKEDC" H 8000 2550 50  0001 C CNN "MPN"
F 5 "C25744" H 8000 2550 50  0001 C CNN "LCSC Part #"
	1    8000 2550
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 5E3C83AC
P 7800 2550
AR Path="/5E2D92F4/5E3C83AC" Ref="R?"  Part="1" 
AR Path="/6062DC24/5E3C83AC" Ref="R39"  Part="1" 
F 0 "R39" V 7700 2600 50  0000 C CNN
F 1 "10k" V 7800 2550 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 7730 2550 50  0001 C CNN
F 3 "~" H 7800 2550 50  0001 C CNN
F 4 "CRCW040210K0FKEDC" H 7800 2550 50  0001 C CNN "MPN"
F 5 "C25744" H 7800 2550 50  0001 C CNN "LCSC Part #"
	1    7800 2550
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 605E5EBC
P 2450 1350
AR Path="/5E2D92F4/605E5EBC" Ref="R?"  Part="1" 
AR Path="/6062DC24/605E5EBC" Ref="R26"  Part="1" 
F 0 "R26" V 2350 1400 50  0000 C CNN
F 1 "1k" V 2450 1350 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 2380 1350 50  0001 C CNN
F 3 "~" H 2450 1350 50  0001 C CNN
F 4 "ERJ-2RKF1001X" H 2450 1350 50  0001 C CNN "MPN"
F 5 "C11702" H 2450 1350 50  0001 C CNN "LCSC Part #"
	1    2450 1350
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 605E5EC5
P 2500 2200
AR Path="/5E2D92F4/605E5EC5" Ref="R?"  Part="1" 
AR Path="/6062DC24/605E5EC5" Ref="R27"  Part="1" 
F 0 "R27" V 2400 2200 50  0000 C CNN
F 1 "18k" V 2500 2200 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 2430 2200 50  0001 C CNN
F 3 "~" H 2500 2200 50  0001 C CNN
F 4 "CRCW040218K0FKED" H 2500 2200 50  0001 C CNN "MPN"
F 5 "C25762" H 2500 2200 50  0001 C CNN "LCSC Part #"
	1    2500 2200
	0    1    1    0   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 605E5EA6
P 3200 4900
AR Path="/5E2D92F4/605E5EA6" Ref="C?"  Part="1" 
AR Path="/6062DC24/605E5EA6" Ref="C22"  Part="1" 
F 0 "C22" V 3100 4800 50  0000 C CNN
F 1 "15nF 50V" V 3300 4850 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 3200 4900 50  0001 C CNN
F 3 "~" H 3200 4900 50  0001 C CNN
F 4 "GCM155R71E153JA55D" H 3200 4900 50  0001 C CNN "MPN"
F 5 "" H 3200 4900 50  0001 C CNN "LCSC Part #"
	1    3200 4900
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 605E5EAB
P 3450 4850
AR Path="/5E2D92F4/605E5EAB" Ref="R?"  Part="1" 
AR Path="/6062DC24/605E5EAB" Ref="R30"  Part="1" 
F 0 "R30" H 3380 4804 50  0000 R CNN
F 1 "3.3k" H 3380 4895 50  0000 R CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 3380 4850 50  0001 C CNN
F 3 "~" H 3450 4850 50  0001 C CNN
F 4 "CRCW04023K30FKEDC" H 3450 4850 50  0001 C CNN "MPN"
F 5 "C25890" H 3450 4850 50  0001 C CNN "LCSC Part #"
	1    3450 4850
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 605E5EC8
P 6300 4350
AR Path="/5E2D92F4/605E5EC8" Ref="R?"  Part="1" 
AR Path="/6062DC24/605E5EC8" Ref="R37"  Part="1" 
F 0 "R37" V 6400 4350 50  0000 C CNN
F 1 "22R 1%" V 6200 4300 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 6230 4350 50  0001 C CNN
F 3 "~" H 6300 4350 50  0001 C CNN
F 4 "CRCW040222R0FKEDC" H 6300 4350 50  0001 C CNN "MPN"
F 5 "C25092" H 6300 4350 50  0001 C CNN "LCSC Part #"
	1    6300 4350
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 605E5EC9
P 6350 4950
AR Path="/5E2D92F4/605E5EC9" Ref="R?"  Part="1" 
AR Path="/6062DC24/605E5EC9" Ref="R38"  Part="1" 
F 0 "R38" V 6450 4950 50  0000 C CNN
F 1 "22R 1%" V 6250 4900 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 6280 4950 50  0001 C CNN
F 3 "~" H 6350 4950 50  0001 C CNN
F 4 "CRCW040222R0FKEDC" H 6350 4950 50  0001 C CNN "MPN"
F 5 "C25092" H 6350 4950 50  0001 C CNN "LCSC Part #"
	1    6350 4950
	0    -1   -1   0   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 605E5ECA
P 6750 5050
AR Path="/5E2D92F4/605E5ECA" Ref="C?"  Part="1" 
AR Path="/6062DC24/605E5ECA" Ref="C28"  Part="1" 
F 0 "C28" H 6600 5050 50  0000 C CNN
F 1 "2.2nF 50V" H 6450 5150 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 6750 5050 50  0001 C CNN
F 3 "~" H 6750 5050 50  0001 C CNN
F 4 "C0402C222J3GEC7411" H 6750 5050 50  0001 C CNN "MPN"
F 5 "C1531" H 6750 5050 50  0001 C CNN "LCSC Part #"
	1    6750 5050
	-1   0    0    1   
$EndComp
$Comp
L Device:Thermistor TH?
U 1 1 5E49E046
P 9650 2250
AR Path="/5E2D92F4/5E49E046" Ref="TH?"  Part="1" 
AR Path="/6062DC24/5E49E046" Ref="TH2"  Part="1" 
F 0 "TH2" H 9755 2296 50  0000 L CNN
F 1 "10k" H 9755 2205 50  0000 L CNN
F 2 "Resistor_SMD:R_0402_1005Metric" H 9650 2250 50  0001 C CNN
F 3 "~" H 9650 2250 50  0001 C CNN
F 4 "CRCW040210K0FKEDC" H 9650 2250 50  0001 C CNN "MPN"
	1    9650 2250
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 5E49F539
P 9650 2650
AR Path="/5E2D92F4/5E49F539" Ref="R?"  Part="1" 
AR Path="/6062DC24/5E49F539" Ref="R42"  Part="1" 
F 0 "R42" H 9580 2604 50  0000 R CNN
F 1 "3.3k" H 9580 2695 50  0000 R CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 9580 2650 50  0001 C CNN
F 3 "~" H 9650 2650 50  0001 C CNN
F 4 "CRCW04023K30FKEDC" H 9650 2650 50  0001 C CNN "MPN"
F 5 "C25890" H 9650 2650 50  0001 C CNN "LCSC Part #"
	1    9650 2650
	-1   0    0    1   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 5E49FE0F
P 9350 2700
AR Path="/5E2D92F4/5E49FE0F" Ref="C?"  Part="1" 
AR Path="/6062DC24/5E49FE0F" Ref="C38"  Part="1" 
F 0 "C38" V 9300 2750 50  0000 L CNN
F 1 "2.2uF 25V" V 9200 2550 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 9350 2700 50  0001 C CNN
F 3 "~" H 9350 2700 50  0001 C CNN
F 4 "GRM155C81E225KE11D" H 9350 2700 50  0001 C CNN "MPN"
F 5 "C12530" H 9350 2700 50  0001 C CNN "LCSC Part #"
	1    9350 2700
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 609AF570
P 4000 7245
AR Path="/5E2D92F4/609AF570" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF570" Ref="R32"  Part="1" 
F 0 "R32" V 4100 7295 50  0000 R CNN
F 1 "500uOhm 6W 1%" V 3900 7545 50  0000 R CNN
F 2 "Resistor_SMD:R_2512_6332Metric" V 3930 7245 50  0001 C CNN
F 3 "~" H 4000 7245 50  0001 C CNN
F 4 "CSS2H-2512R-L500F" H 4000 7245 50  0001 C CNN "MPN"
	1    4000 7245
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 609AF577
P 2000 5700
AR Path="/5E2D92F4/609AF577" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF577" Ref="R24"  Part="1" 
F 0 "R24" V 2100 5700 50  0000 C CNN
F 1 "2R2" V 2000 5700 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 1930 5700 50  0001 C CNN
F 3 "~" H 2000 5700 50  0001 C CNN
F 4 "CRCW04022R20FKEDC" H 2000 5700 50  0001 C CNN "MPN"
	1    2000 5700
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 609AF57E
P 2000 6450
AR Path="/5E2D92F4/609AF57E" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF57E" Ref="R25"  Part="1" 
F 0 "R25" V 2100 6450 50  0000 C CNN
F 1 "2R2" V 2000 6450 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 1930 6450 50  0001 C CNN
F 3 "~" H 2000 6450 50  0001 C CNN
F 4 "CRCW04022R20FKEDC" H 2000 6450 50  0001 C CNN "MPN"
	1    2000 6450
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 609AF585
P 3325 6440
AR Path="/5E2D92F4/609AF585" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF585" Ref="R29"  Part="1" 
F 0 "R29" V 3425 6440 50  0000 C CNN
F 1 "2R2" V 3325 6440 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 3255 6440 50  0001 C CNN
F 3 "~" H 3325 6440 50  0001 C CNN
F 4 "CRCW04022R20FKEDC" H 3325 6440 50  0001 C CNN "MPN"
	1    3325 6440
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 609AF58C
P 3325 5700
AR Path="/5E2D92F4/609AF58C" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF58C" Ref="R28"  Part="1" 
F 0 "R28" V 3425 5700 50  0000 C CNN
F 1 "2R2" V 3325 5700 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 3255 5700 50  0001 C CNN
F 3 "~" H 3325 5700 50  0001 C CNN
F 4 "CRCW04022R20FKEDC" H 3325 5700 50  0001 C CNN "MPN"
	1    3325 5700
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 609AF597
P 5050 5700
AR Path="/5E2D92F4/609AF597" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF597" Ref="R33"  Part="1" 
F 0 "R33" V 5150 5700 50  0000 C CNN
F 1 "2R2" V 5050 5700 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 4980 5700 50  0001 C CNN
F 3 "~" H 5050 5700 50  0001 C CNN
F 4 "CRCW04022R20FKEDC" H 5050 5700 50  0001 C CNN "MPN"
	1    5050 5700
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 609AF5A2
P 5050 6450
AR Path="/5E2D92F4/609AF5A2" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF5A2" Ref="R34"  Part="1" 
F 0 "R34" V 5150 6450 50  0000 C CNN
F 1 "2R2" V 5050 6450 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 4980 6450 50  0001 C CNN
F 3 "~" H 5050 6450 50  0001 C CNN
F 4 "CRCW04022R20FKEDC" H 5050 6450 50  0001 C CNN "MPN"
	1    5050 6450
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R?
U 1 1 609AF5AE
P 5500 7200
AR Path="/5E2D92F4/609AF5AE" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF5AE" Ref="R36"  Part="1" 
F 0 "R36" H 5400 7150 50  0000 R CNN
F 1 "500uOhm 6W 1%" H 5400 7250 50  0000 R CNN
F 2 "Resistor_SMD:R_2512_6332Metric" V 5430 7200 50  0001 C CNN
F 3 "~" H 5500 7200 50  0001 C CNN
F 4 "CSS2H-2512R-L500F" H 5500 7200 50  0001 C CNN "MPN"
	1    5500 7200
	-1   0    0    1   
$EndComp
$Comp
L bldc_motor_cntroller-rescue:Net-Tie_2-Device NT?
U 1 1 609AF5C7
P 3700 7095
AR Path="/5E2D92F4/609AF5C7" Ref="NT?"  Part="1" 
AR Path="/6062DC24/609AF5C7" Ref="NT5"  Part="1" 
F 0 "NT5" H 3700 7184 50  0000 C CNN
F 1 "Net-Tie_2" H 3700 7185 50  0001 C CNN
F 2 "NetTie:NetTie-2_SMD_Pad0.5mm" H 3700 7095 50  0001 C CNN
F 3 "~" H 3700 7095 50  0001 C CNN
F 4 "-" H 3700 7095 50  0001 C CNN "MPN"
	1    3700 7095
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:Net-Tie_2-Device NT?
U 1 1 609AF5D6
P 3700 7395
AR Path="/5E2D92F4/609AF5D6" Ref="NT?"  Part="1" 
AR Path="/6062DC24/609AF5D6" Ref="NT6"  Part="1" 
F 0 "NT6" H 3700 7484 50  0000 C CNN
F 1 "Net-Tie_2" H 3700 7485 50  0001 C CNN
F 2 "NetTie:NetTie-2_SMD_Pad0.5mm" H 3700 7395 50  0001 C CNN
F 3 "~" H 3700 7395 50  0001 C CNN
F 4 "-" H 3700 7395 50  0001 C CNN "MPN"
	1    3700 7395
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:Net-Tie_2-Device NT?
U 1 1 609AF5DF
P 5400 7050
AR Path="/5E2D92F4/609AF5DF" Ref="NT?"  Part="1" 
AR Path="/6062DC24/609AF5DF" Ref="NT7"  Part="1" 
F 0 "NT7" H 5350 7100 50  0000 C CNN
F 1 "Net-Tie_2" H 5400 7140 50  0001 C CNN
F 2 "NetTie:NetTie-2_SMD_Pad0.5mm" H 5400 7050 50  0001 C CNN
F 3 "~" H 5400 7050 50  0001 C CNN
F 4 "-" H 5400 7050 50  0001 C CNN "MPN"
	1    5400 7050
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:Net-Tie_2-Device NT?
U 1 1 609AF5E6
P 5400 7350
AR Path="/5E2D92F4/609AF5E6" Ref="NT?"  Part="1" 
AR Path="/6062DC24/609AF5E6" Ref="NT8"  Part="1" 
F 0 "NT8" H 5350 7250 50  0000 C CNN
F 1 "Net-Tie_2" H 5400 7440 50  0001 C CNN
F 2 "NetTie:NetTie-2_SMD_Pad0.5mm" H 5400 7350 50  0001 C CNN
F 3 "~" H 5400 7350 50  0001 C CNN
F 4 "-" H 5400 7350 50  0001 C CNN "MPN"
	1    5400 7350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R?
U 1 1 609AF5EF
P 3450 7095
AR Path="/5E2D92F4/609AF5EF" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF5EF" Ref="R31"  Part="1" 
F 0 "R31" V 3350 7145 50  0000 C CNN
F 1 "120R" V 3450 7095 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 3380 7095 50  0001 C CNN
F 3 "~" H 3450 7095 50  0001 C CNN
F 4 "ERJ-2RKF1200X" H 3450 7095 50  0001 C CNN "MPN"
F 5 "C25079" H 3450 7095 50  0001 C CNN "LCSC Part #"
	1    3450 7095
	0    -1   -1   0   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 609AF5FA
P 3200 7245
AR Path="/5E2D92F4/609AF5FA" Ref="C?"  Part="1" 
AR Path="/6062DC24/609AF5FA" Ref="C23"  Part="1" 
F 0 "C23" H 3350 7195 50  0000 C CNN
F 1 "2.2nF 50V" H 3100 7345 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 3200 7245 50  0001 C CNN
F 3 "~" H 3200 7245 50  0001 C CNN
F 4 "C0402C222J3GEC7411" H 3200 7245 50  0001 C CNN "MPN"
F 5 "C1531" H 3200 7245 50  0001 C CNN "LCSC Part #"
	1    3200 7245
	-1   0    0    1   
$EndComp
$Comp
L Device:R R?
U 1 1 609AF60B
P 5150 7050
AR Path="/5E2D92F4/609AF60B" Ref="R?"  Part="1" 
AR Path="/6062DC24/609AF60B" Ref="R35"  Part="1" 
F 0 "R35" V 5050 7100 50  0000 C CNN
F 1 "120R" V 5150 7050 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 5080 7050 50  0001 C CNN
F 3 "~" H 5150 7050 50  0001 C CNN
F 4 "ERJ-2RKF1200X" H 5150 7050 50  0001 C CNN "MPN"
F 5 "C25079" H 5150 7050 50  0001 C CNN "LCSC Part #"
	1    5150 7050
	0    -1   -1   0   
$EndComp
$Comp
L Device:C_Small C?
U 1 1 609AF612
P 4900 7200
AR Path="/5E2D92F4/609AF612" Ref="C?"  Part="1" 
AR Path="/6062DC24/609AF612" Ref="C24"  Part="1" 
F 0 "C24" H 5050 7150 50  0000 C CNN
F 1 "2.2nF 50V" H 4800 7300 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 4900 7200 50  0001 C CNN
F 3 "~" H 4900 7200 50  0001 C CNN
F 4 "C0402C222J3GEC7411" H 4900 7200 50  0001 C CNN "MPN"
F 5 "C1531" H 4900 7200 50  0001 C CNN "LCSC Part #"
	1    4900 7200
	-1   0    0    1   
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J?
U 1 1 609AF697
P 7250 6100
AR Path="/5E2D92F4/609AF697" Ref="J?"  Part="1" 
AR Path="/6062DC24/609AF697" Ref="J2"  Part="1" 
F 0 "J2" H 7330 6142 50  0000 L CNN
F 1 "MR30PW-M 15A (30A)" H 7330 6051 50  0000 L CNN
F 2 "Connector_AMASS:AMASS_MR30PW-M_1x03_P3.50mm_Horizontal" H 7250 6100 50  0001 C CNN
F 3 "~" H 7250 6100 50  0001 C CNN
F 4 "-" H 7250 6100 50  0001 C CNN "MPN"
	1    7250 6100
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:IRF7480MTRPBF-MG-WDSON-8 Q?
U 1 1 609AF6D0
P 2100 5700
AR Path="/5E2D92F4/609AF6D0" Ref="Q?"  Part="1" 
AR Path="/6062DC24/609AF6D0" Ref="Q7"  Part="1" 
AR Path="/609AF6D0" Ref="Q?"  Part="1" 
F 0 "Q7" H 2375 5840 50  0000 L CNN
F 1 "IRF7480MTRPBF" H 2290 5545 50  0000 L CNN
F 2 "MG-WDSON-8:Infineon-MG-WDSON-8-05_2016-901-MFG" H 2100 6300 50  0001 L CNN
F 3 "https://www.infineon.com/dgdl/Infineon-IRF7480M-DS-v01_02-EN.pdf?fileId=5546d462533600a4015355ff8fa41c30" H 2100 6400 50  0001 L CNN
F 4 "No" H 2100 6500 50  0001 L CNN "automotive"
F 5 "Trans" H 2100 6600 50  0001 L CNN "category"
F 6 "217A" H 2100 6700 50  0001 L CNN "continuous drain current"
F 7 "False" H 2100 6800 50  0001 L CNN "depletion mode"
F 8 "Discrete Semiconductors" H 2100 6900 50  0001 L CNN "device class L1"
F 9 "Transistors" H 2100 7000 50  0001 L CNN "device class L2"
F 10 "MOSFETs" H 2100 7100 50  0001 L CNN "device class L3"
F 11 "MOSFET N-CH 40V 217A DIRECTFET" H 2100 7200 50  0001 L CNN "digikey description"
F 12 "IRF7480MTRPBFCT-ND" H 2100 7300 50  0001 L CNN "digikey part number"
F 13 "40V" H 2100 7400 50  0001 L CNN "drain to source breakdown voltage"
F 14 "0.95mΩ" H 2100 7500 50  0001 L CNN "drain to source resistance"
F 15 "40V" H 2100 7600 50  0001 L CNN "drain to source voltage"
F 16 "https://www.infineon.com/dgdl/Infineon-AN-1035-ApplicationNotes-v29_01-EN.pdf?fileId=5546d462533600a40153559159020f76" H 2100 7700 50  0001 L CNN "footprint url"
F 17 "123nC @ 10V" H 2100 7800 50  0001 L CNN "gate charge at vgs"
F 18 "20V" H 2100 7900 50  0001 L CNN "gate to source voltage"
F 19 "0.7mm" H 2100 8000 50  0001 L CNN "height"
F 20 "6680pF @ 25V" H 2100 8100 50  0001 L CNN "input capacitace at vds"
F 21 "Yes" H 2100 8200 50  0001 L CNN "lead free"
F 22 "f08410abc2d010b0" H 2100 8300 50  0001 L CNN "library id"
F 23 "Infineon" H 2100 8400 50  0001 L CNN "manufacturer"
F 24 "1.2V" H 2100 8500 50  0001 L CNN "max forward diode voltage"
F 25 "+150°C" H 2100 8600 50  0001 L CNN "max junction temp"
F 26 "942-IRF7480MTRPBF" H 2100 8700 50  0001 L CNN "mouser part number"
F 27 "1" H 2100 8800 50  0001 L CNN "number of N channels"
F 28 "1" H 2100 8900 50  0001 L CNN "number of channels"
F 29 "DirectFET_ME" H 2100 9000 50  0001 L CNN "package"
F 30 "96W" H 2100 9100 50  0001 L CNN "power dissipation"
F 31 "868A" H 2100 9200 50  0001 L CNN "pulse drain current"
F 32 "56nC" H 2100 9300 50  0001 L CNN "reverse recovery charge"
F 33 "44ns" H 2100 9400 50  0001 L CNN "reverse recovery time"
F 34 "Yes" H 2100 9500 50  0001 L CNN "rohs"
F 35 "20°C/W" H 2100 9600 50  0001 L CNN "rthja max"
F 36 "0.02mm" H 2100 9700 50  0001 L CNN "standoff height"
F 37 "+150°C" H 2100 9800 50  0001 L CNN "temperature range high"
F 38 "-55°C" H 2100 9900 50  0001 L CNN "temperature range low"
F 39 "3.9V" H 2100 10000 50  0001 L CNN "threshold vgs max"
F 40 "2.1V" H 2100 10100 50  0001 L CNN "threshold vgs min"
F 41 "68ns" H 2100 10200 50  0001 L CNN "turn off delay time"
F 42 "21ns" H 2100 10300 50  0001 L CNN "turn on delay time"
	1    2100 5700
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:IRF7480MTRPBF-MG-WDSON-8 Q?
U 1 1 609AF70E
P 3400 5700
AR Path="/5E2D92F4/609AF70E" Ref="Q?"  Part="1" 
AR Path="/6062DC24/609AF70E" Ref="Q9"  Part="1" 
AR Path="/609AF70E" Ref="Q?"  Part="1" 
F 0 "Q9" H 3675 5840 50  0000 L CNN
F 1 "IRF7480MTRPBF" H 3590 5545 50  0000 L CNN
F 2 "MG-WDSON-8:Infineon-MG-WDSON-8-05_2016-901-MFG" H 3400 6300 50  0001 L CNN
F 3 "https://www.infineon.com/dgdl/Infineon-IRF7480M-DS-v01_02-EN.pdf?fileId=5546d462533600a4015355ff8fa41c30" H 3400 6400 50  0001 L CNN
F 4 "No" H 3400 6500 50  0001 L CNN "automotive"
F 5 "Trans" H 3400 6600 50  0001 L CNN "category"
F 6 "217A" H 3400 6700 50  0001 L CNN "continuous drain current"
F 7 "False" H 3400 6800 50  0001 L CNN "depletion mode"
F 8 "Discrete Semiconductors" H 3400 6900 50  0001 L CNN "device class L1"
F 9 "Transistors" H 3400 7000 50  0001 L CNN "device class L2"
F 10 "MOSFETs" H 3400 7100 50  0001 L CNN "device class L3"
F 11 "MOSFET N-CH 40V 217A DIRECTFET" H 3400 7200 50  0001 L CNN "digikey description"
F 12 "IRF7480MTRPBFCT-ND" H 3400 7300 50  0001 L CNN "digikey part number"
F 13 "40V" H 3400 7400 50  0001 L CNN "drain to source breakdown voltage"
F 14 "0.95mΩ" H 3400 7500 50  0001 L CNN "drain to source resistance"
F 15 "40V" H 3400 7600 50  0001 L CNN "drain to source voltage"
F 16 "https://www.infineon.com/dgdl/Infineon-AN-1035-ApplicationNotes-v29_01-EN.pdf?fileId=5546d462533600a40153559159020f76" H 3400 7700 50  0001 L CNN "footprint url"
F 17 "123nC @ 10V" H 3400 7800 50  0001 L CNN "gate charge at vgs"
F 18 "20V" H 3400 7900 50  0001 L CNN "gate to source voltage"
F 19 "0.7mm" H 3400 8000 50  0001 L CNN "height"
F 20 "6680pF @ 25V" H 3400 8100 50  0001 L CNN "input capacitace at vds"
F 21 "Yes" H 3400 8200 50  0001 L CNN "lead free"
F 22 "f08410abc2d010b0" H 3400 8300 50  0001 L CNN "library id"
F 23 "Infineon" H 3400 8400 50  0001 L CNN "manufacturer"
F 24 "1.2V" H 3400 8500 50  0001 L CNN "max forward diode voltage"
F 25 "+150°C" H 3400 8600 50  0001 L CNN "max junction temp"
F 26 "942-IRF7480MTRPBF" H 3400 8700 50  0001 L CNN "mouser part number"
F 27 "1" H 3400 8800 50  0001 L CNN "number of N channels"
F 28 "1" H 3400 8900 50  0001 L CNN "number of channels"
F 29 "DirectFET_ME" H 3400 9000 50  0001 L CNN "package"
F 30 "96W" H 3400 9100 50  0001 L CNN "power dissipation"
F 31 "868A" H 3400 9200 50  0001 L CNN "pulse drain current"
F 32 "56nC" H 3400 9300 50  0001 L CNN "reverse recovery charge"
F 33 "44ns" H 3400 9400 50  0001 L CNN "reverse recovery time"
F 34 "Yes" H 3400 9500 50  0001 L CNN "rohs"
F 35 "20°C/W" H 3400 9600 50  0001 L CNN "rthja max"
F 36 "0.02mm" H 3400 9700 50  0001 L CNN "standoff height"
F 37 "+150°C" H 3400 9800 50  0001 L CNN "temperature range high"
F 38 "-55°C" H 3400 9900 50  0001 L CNN "temperature range low"
F 39 "3.9V" H 3400 10000 50  0001 L CNN "threshold vgs max"
F 40 "2.1V" H 3400 10100 50  0001 L CNN "threshold vgs min"
F 41 "68ns" H 3400 10200 50  0001 L CNN "turn off delay time"
F 42 "21ns" H 3400 10300 50  0001 L CNN "turn on delay time"
	1    3400 5700
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:IRF7480MTRPBF-MG-WDSON-8 Q?
U 1 1 609AF73F
P 2100 6450
AR Path="/5E2D92F4/609AF73F" Ref="Q?"  Part="1" 
AR Path="/6062DC24/609AF73F" Ref="Q8"  Part="1" 
AR Path="/609AF73F" Ref="Q?"  Part="1" 
F 0 "Q8" H 2375 6590 50  0000 L CNN
F 1 "IRF7480MTRPBF" H 2290 6295 50  0000 L CNN
F 2 "MG-WDSON-8:Infineon-MG-WDSON-8-05_2016-901-MFG" H 2100 7050 50  0001 L CNN
F 3 "https://www.infineon.com/dgdl/Infineon-IRF7480M-DS-v01_02-EN.pdf?fileId=5546d462533600a4015355ff8fa41c30" H 2100 7150 50  0001 L CNN
F 4 "No" H 2100 7250 50  0001 L CNN "automotive"
F 5 "Trans" H 2100 7350 50  0001 L CNN "category"
F 6 "217A" H 2100 7450 50  0001 L CNN "continuous drain current"
F 7 "False" H 2100 7550 50  0001 L CNN "depletion mode"
F 8 "Discrete Semiconductors" H 2100 7650 50  0001 L CNN "device class L1"
F 9 "Transistors" H 2100 7750 50  0001 L CNN "device class L2"
F 10 "MOSFETs" H 2100 7850 50  0001 L CNN "device class L3"
F 11 "MOSFET N-CH 40V 217A DIRECTFET" H 2100 7950 50  0001 L CNN "digikey description"
F 12 "IRF7480MTRPBFCT-ND" H 2100 8050 50  0001 L CNN "digikey part number"
F 13 "40V" H 2100 8150 50  0001 L CNN "drain to source breakdown voltage"
F 14 "0.95mΩ" H 2100 8250 50  0001 L CNN "drain to source resistance"
F 15 "40V" H 2100 8350 50  0001 L CNN "drain to source voltage"
F 16 "https://www.infineon.com/dgdl/Infineon-AN-1035-ApplicationNotes-v29_01-EN.pdf?fileId=5546d462533600a40153559159020f76" H 2100 8450 50  0001 L CNN "footprint url"
F 17 "123nC @ 10V" H 2100 8550 50  0001 L CNN "gate charge at vgs"
F 18 "20V" H 2100 8650 50  0001 L CNN "gate to source voltage"
F 19 "0.7mm" H 2100 8750 50  0001 L CNN "height"
F 20 "6680pF @ 25V" H 2100 8850 50  0001 L CNN "input capacitace at vds"
F 21 "Yes" H 2100 8950 50  0001 L CNN "lead free"
F 22 "f08410abc2d010b0" H 2100 9050 50  0001 L CNN "library id"
F 23 "Infineon" H 2100 9150 50  0001 L CNN "manufacturer"
F 24 "1.2V" H 2100 9250 50  0001 L CNN "max forward diode voltage"
F 25 "+150°C" H 2100 9350 50  0001 L CNN "max junction temp"
F 26 "942-IRF7480MTRPBF" H 2100 9450 50  0001 L CNN "mouser part number"
F 27 "1" H 2100 9550 50  0001 L CNN "number of N channels"
F 28 "1" H 2100 9650 50  0001 L CNN "number of channels"
F 29 "DirectFET_ME" H 2100 9750 50  0001 L CNN "package"
F 30 "96W" H 2100 9850 50  0001 L CNN "power dissipation"
F 31 "868A" H 2100 9950 50  0001 L CNN "pulse drain current"
F 32 "56nC" H 2100 10050 50  0001 L CNN "reverse recovery charge"
F 33 "44ns" H 2100 10150 50  0001 L CNN "reverse recovery time"
F 34 "Yes" H 2100 10250 50  0001 L CNN "rohs"
F 35 "20°C/W" H 2100 10350 50  0001 L CNN "rthja max"
F 36 "0.02mm" H 2100 10450 50  0001 L CNN "standoff height"
F 37 "+150°C" H 2100 10550 50  0001 L CNN "temperature range high"
F 38 "-55°C" H 2100 10650 50  0001 L CNN "temperature range low"
F 39 "3.9V" H 2100 10750 50  0001 L CNN "threshold vgs max"
F 40 "2.1V" H 2100 10850 50  0001 L CNN "threshold vgs min"
F 41 "68ns" H 2100 10950 50  0001 L CNN "turn off delay time"
F 42 "21ns" H 2100 11050 50  0001 L CNN "turn on delay time"
	1    2100 6450
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:IRF7480MTRPBF-MG-WDSON-8 Q?
U 1 1 609AF76C
P 3400 6440
AR Path="/5E2D92F4/609AF76C" Ref="Q?"  Part="1" 
AR Path="/6062DC24/609AF76C" Ref="Q10"  Part="1" 
AR Path="/609AF76C" Ref="Q?"  Part="1" 
F 0 "Q10" H 3675 6580 50  0000 L CNN
F 1 "IRF7480MTRPBF" H 3590 6285 50  0000 L CNN
F 2 "MG-WDSON-8:Infineon-MG-WDSON-8-05_2016-901-MFG" H 3400 7040 50  0001 L CNN
F 3 "https://www.infineon.com/dgdl/Infineon-IRF7480M-DS-v01_02-EN.pdf?fileId=5546d462533600a4015355ff8fa41c30" H 3400 7140 50  0001 L CNN
F 4 "No" H 3400 7240 50  0001 L CNN "automotive"
F 5 "Trans" H 3400 7340 50  0001 L CNN "category"
F 6 "217A" H 3400 7440 50  0001 L CNN "continuous drain current"
F 7 "False" H 3400 7540 50  0001 L CNN "depletion mode"
F 8 "Discrete Semiconductors" H 3400 7640 50  0001 L CNN "device class L1"
F 9 "Transistors" H 3400 7740 50  0001 L CNN "device class L2"
F 10 "MOSFETs" H 3400 7840 50  0001 L CNN "device class L3"
F 11 "MOSFET N-CH 40V 217A DIRECTFET" H 3400 7940 50  0001 L CNN "digikey description"
F 12 "IRF7480MTRPBFCT-ND" H 3400 8040 50  0001 L CNN "digikey part number"
F 13 "40V" H 3400 8140 50  0001 L CNN "drain to source breakdown voltage"
F 14 "0.95mΩ" H 3400 8240 50  0001 L CNN "drain to source resistance"
F 15 "40V" H 3400 8340 50  0001 L CNN "drain to source voltage"
F 16 "https://www.infineon.com/dgdl/Infineon-AN-1035-ApplicationNotes-v29_01-EN.pdf?fileId=5546d462533600a40153559159020f76" H 3400 8440 50  0001 L CNN "footprint url"
F 17 "123nC @ 10V" H 3400 8540 50  0001 L CNN "gate charge at vgs"
F 18 "20V" H 3400 8640 50  0001 L CNN "gate to source voltage"
F 19 "0.7mm" H 3400 8740 50  0001 L CNN "height"
F 20 "6680pF @ 25V" H 3400 8840 50  0001 L CNN "input capacitace at vds"
F 21 "Yes" H 3400 8940 50  0001 L CNN "lead free"
F 22 "f08410abc2d010b0" H 3400 9040 50  0001 L CNN "library id"
F 23 "Infineon" H 3400 9140 50  0001 L CNN "manufacturer"
F 24 "1.2V" H 3400 9240 50  0001 L CNN "max forward diode voltage"
F 25 "+150°C" H 3400 9340 50  0001 L CNN "max junction temp"
F 26 "942-IRF7480MTRPBF" H 3400 9440 50  0001 L CNN "mouser part number"
F 27 "1" H 3400 9540 50  0001 L CNN "number of N channels"
F 28 "1" H 3400 9640 50  0001 L CNN "number of channels"
F 29 "DirectFET_ME" H 3400 9740 50  0001 L CNN "package"
F 30 "96W" H 3400 9840 50  0001 L CNN "power dissipation"
F 31 "868A" H 3400 9940 50  0001 L CNN "pulse drain current"
F 32 "56nC" H 3400 10040 50  0001 L CNN "reverse recovery charge"
F 33 "44ns" H 3400 10140 50  0001 L CNN "reverse recovery time"
F 34 "Yes" H 3400 10240 50  0001 L CNN "rohs"
F 35 "20°C/W" H 3400 10340 50  0001 L CNN "rthja max"
F 36 "0.02mm" H 3400 10440 50  0001 L CNN "standoff height"
F 37 "+150°C" H 3400 10540 50  0001 L CNN "temperature range high"
F 38 "-55°C" H 3400 10640 50  0001 L CNN "temperature range low"
F 39 "3.9V" H 3400 10740 50  0001 L CNN "threshold vgs max"
F 40 "2.1V" H 3400 10840 50  0001 L CNN "threshold vgs min"
F 41 "68ns" H 3400 10940 50  0001 L CNN "turn off delay time"
F 42 "21ns" H 3400 11040 50  0001 L CNN "turn on delay time"
	1    3400 6440
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:IRF7480MTRPBF-MG-WDSON-8 Q?
U 1 1 609AF799
P 5100 6450
AR Path="/5E2D92F4/609AF799" Ref="Q?"  Part="1" 
AR Path="/6062DC24/609AF799" Ref="Q12"  Part="1" 
AR Path="/609AF799" Ref="Q?"  Part="1" 
F 0 "Q12" H 5375 6590 50  0000 L CNN
F 1 "IRF7480MTRPBF" H 5290 6295 50  0000 L CNN
F 2 "MG-WDSON-8:Infineon-MG-WDSON-8-05_2016-901-MFG" H 5100 7050 50  0001 L CNN
F 3 "https://www.infineon.com/dgdl/Infineon-IRF7480M-DS-v01_02-EN.pdf?fileId=5546d462533600a4015355ff8fa41c30" H 5100 7150 50  0001 L CNN
F 4 "No" H 5100 7250 50  0001 L CNN "automotive"
F 5 "Trans" H 5100 7350 50  0001 L CNN "category"
F 6 "217A" H 5100 7450 50  0001 L CNN "continuous drain current"
F 7 "False" H 5100 7550 50  0001 L CNN "depletion mode"
F 8 "Discrete Semiconductors" H 5100 7650 50  0001 L CNN "device class L1"
F 9 "Transistors" H 5100 7750 50  0001 L CNN "device class L2"
F 10 "MOSFETs" H 5100 7850 50  0001 L CNN "device class L3"
F 11 "MOSFET N-CH 40V 217A DIRECTFET" H 5100 7950 50  0001 L CNN "digikey description"
F 12 "IRF7480MTRPBFCT-ND" H 5100 8050 50  0001 L CNN "digikey part number"
F 13 "40V" H 5100 8150 50  0001 L CNN "drain to source breakdown voltage"
F 14 "0.95mΩ" H 5100 8250 50  0001 L CNN "drain to source resistance"
F 15 "40V" H 5100 8350 50  0001 L CNN "drain to source voltage"
F 16 "https://www.infineon.com/dgdl/Infineon-AN-1035-ApplicationNotes-v29_01-EN.pdf?fileId=5546d462533600a40153559159020f76" H 5100 8450 50  0001 L CNN "footprint url"
F 17 "123nC @ 10V" H 5100 8550 50  0001 L CNN "gate charge at vgs"
F 18 "20V" H 5100 8650 50  0001 L CNN "gate to source voltage"
F 19 "0.7mm" H 5100 8750 50  0001 L CNN "height"
F 20 "6680pF @ 25V" H 5100 8850 50  0001 L CNN "input capacitace at vds"
F 21 "Yes" H 5100 8950 50  0001 L CNN "lead free"
F 22 "f08410abc2d010b0" H 5100 9050 50  0001 L CNN "library id"
F 23 "Infineon" H 5100 9150 50  0001 L CNN "manufacturer"
F 24 "1.2V" H 5100 9250 50  0001 L CNN "max forward diode voltage"
F 25 "+150°C" H 5100 9350 50  0001 L CNN "max junction temp"
F 26 "942-IRF7480MTRPBF" H 5100 9450 50  0001 L CNN "mouser part number"
F 27 "1" H 5100 9550 50  0001 L CNN "number of N channels"
F 28 "1" H 5100 9650 50  0001 L CNN "number of channels"
F 29 "DirectFET_ME" H 5100 9750 50  0001 L CNN "package"
F 30 "96W" H 5100 9850 50  0001 L CNN "power dissipation"
F 31 "868A" H 5100 9950 50  0001 L CNN "pulse drain current"
F 32 "56nC" H 5100 10050 50  0001 L CNN "reverse recovery charge"
F 33 "44ns" H 5100 10150 50  0001 L CNN "reverse recovery time"
F 34 "Yes" H 5100 10250 50  0001 L CNN "rohs"
F 35 "20°C/W" H 5100 10350 50  0001 L CNN "rthja max"
F 36 "0.02mm" H 5100 10450 50  0001 L CNN "standoff height"
F 37 "+150°C" H 5100 10550 50  0001 L CNN "temperature range high"
F 38 "-55°C" H 5100 10650 50  0001 L CNN "temperature range low"
F 39 "3.9V" H 5100 10750 50  0001 L CNN "threshold vgs max"
F 40 "2.1V" H 5100 10850 50  0001 L CNN "threshold vgs min"
F 41 "68ns" H 5100 10950 50  0001 L CNN "turn off delay time"
F 42 "21ns" H 5100 11050 50  0001 L CNN "turn on delay time"
	1    5100 6450
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:IRF7480MTRPBF-MG-WDSON-8 Q?
U 1 1 609AF800
P 5100 5700
AR Path="/5E2D92F4/609AF800" Ref="Q?"  Part="1" 
AR Path="/6062DC24/609AF800" Ref="Q11"  Part="1" 
AR Path="/609AF800" Ref="Q?"  Part="1" 
F 0 "Q11" H 5375 5840 50  0000 L CNN
F 1 "IRF7480MTRPBF" H 5290 5545 50  0000 L CNN
F 2 "MG-WDSON-8:Infineon-MG-WDSON-8-05_2016-901-MFG" H 5100 6300 50  0001 L CNN
F 3 "https://www.infineon.com/dgdl/Infineon-IRF7480M-DS-v01_02-EN.pdf?fileId=5546d462533600a4015355ff8fa41c30" H 5100 6400 50  0001 L CNN
F 4 "No" H 5100 6500 50  0001 L CNN "automotive"
F 5 "Trans" H 5100 6600 50  0001 L CNN "category"
F 6 "217A" H 5100 6700 50  0001 L CNN "continuous drain current"
F 7 "False" H 5100 6800 50  0001 L CNN "depletion mode"
F 8 "Discrete Semiconductors" H 5100 6900 50  0001 L CNN "device class L1"
F 9 "Transistors" H 5100 7000 50  0001 L CNN "device class L2"
F 10 "MOSFETs" H 5100 7100 50  0001 L CNN "device class L3"
F 11 "MOSFET N-CH 40V 217A DIRECTFET" H 5100 7200 50  0001 L CNN "digikey description"
F 12 "IRF7480MTRPBFCT-ND" H 5100 7300 50  0001 L CNN "digikey part number"
F 13 "40V" H 5100 7400 50  0001 L CNN "drain to source breakdown voltage"
F 14 "0.95mΩ" H 5100 7500 50  0001 L CNN "drain to source resistance"
F 15 "40V" H 5100 7600 50  0001 L CNN "drain to source voltage"
F 16 "https://www.infineon.com/dgdl/Infineon-AN-1035-ApplicationNotes-v29_01-EN.pdf?fileId=5546d462533600a40153559159020f76" H 5100 7700 50  0001 L CNN "footprint url"
F 17 "123nC @ 10V" H 5100 7800 50  0001 L CNN "gate charge at vgs"
F 18 "20V" H 5100 7900 50  0001 L CNN "gate to source voltage"
F 19 "0.7mm" H 5100 8000 50  0001 L CNN "height"
F 20 "6680pF @ 25V" H 5100 8100 50  0001 L CNN "input capacitace at vds"
F 21 "Yes" H 5100 8200 50  0001 L CNN "lead free"
F 22 "f08410abc2d010b0" H 5100 8300 50  0001 L CNN "library id"
F 23 "Infineon" H 5100 8400 50  0001 L CNN "manufacturer"
F 24 "1.2V" H 5100 8500 50  0001 L CNN "max forward diode voltage"
F 25 "+150°C" H 5100 8600 50  0001 L CNN "max junction temp"
F 26 "942-IRF7480MTRPBF" H 5100 8700 50  0001 L CNN "mouser part number"
F 27 "1" H 5100 8800 50  0001 L CNN "number of N channels"
F 28 "1" H 5100 8900 50  0001 L CNN "number of channels"
F 29 "DirectFET_ME" H 5100 9000 50  0001 L CNN "package"
F 30 "96W" H 5100 9100 50  0001 L CNN "power dissipation"
F 31 "868A" H 5100 9200 50  0001 L CNN "pulse drain current"
F 32 "56nC" H 5100 9300 50  0001 L CNN "reverse recovery charge"
F 33 "44ns" H 5100 9400 50  0001 L CNN "reverse recovery time"
F 34 "Yes" H 5100 9500 50  0001 L CNN "rohs"
F 35 "20°C/W" H 5100 9600 50  0001 L CNN "rthja max"
F 36 "0.02mm" H 5100 9700 50  0001 L CNN "standoff height"
F 37 "+150°C" H 5100 9800 50  0001 L CNN "temperature range high"
F 38 "-55°C" H 5100 9900 50  0001 L CNN "temperature range low"
F 39 "3.9V" H 5100 10000 50  0001 L CNN "threshold vgs max"
F 40 "2.1V" H 5100 10100 50  0001 L CNN "threshold vgs min"
F 41 "68ns" H 5100 10200 50  0001 L CNN "turn off delay time"
F 42 "21ns" H 5100 10300 50  0001 L CNN "turn on delay time"
	1    5100 5700
	1    0    0    -1  
$EndComp
$Comp
L Device:C_Small C?
U 1 1 5E39734B
P 7700 900
AR Path="/5E2D92F4/5E39734B" Ref="C?"  Part="1" 
AR Path="/6062DC24/5E39734B" Ref="C31"  Part="1" 
F 0 "C31" V 7600 750 50  0000 L CNN
F 1 "100nF 50V" V 7800 700 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 7700 900 50  0001 C CNN
F 3 "~" H 7700 900 50  0001 C CNN
F 4 "GRM155R62A104KE14D" H 7700 900 50  0001 C CNN "MPN"
	1    7700 900 
	1    0    0    -1  
$EndComp
$Comp
L bldc_motor_cntroller-rescue:DRV8301DCAR-DRV8301DCAR U?
U 1 1 605E5E7F
P 4450 3050
AR Path="/5E2D92F4/605E5E7F" Ref="U?"  Part="1" 
AR Path="/6062DC24/605E5E7F" Ref="U2"  Part="1" 
F 0 "U2" H 4450 5220 50  0000 C CNN
F 1 "DRV8301DCAR" H 4450 5129 50  0000 C CNN
F 2 "bldc_motor_cntroller:DRV8301DCA" H 4450 3050 50  0001 L BNN
F 3 "F" H 4450 3050 50  0001 L BNN
F 4 "IPC-7351B" H 4450 3050 50  0001 L BNN "Field4"
F 5 "Texas Instruments" H 4450 3050 50  0001 L BNN "Field5"
F 6 "" H 4450 3050 50  0001 L BNN "Field6"
F 7 "DRV8301DCAR" H 4450 3050 50  0001 C CNN "MPN"
	1    4450 3050
	1    0    0    -1  
$EndComp
$Comp
L Device:C_Small C?
U 1 1 605E5ECC
P 6600 4450
AR Path="/5E2D92F4/605E5ECC" Ref="C?"  Part="1" 
AR Path="/6062DC24/605E5ECC" Ref="C27"  Part="1" 
F 0 "C27" H 6450 4450 50  0000 C CNN
F 1 "2.2nF 50V" H 6300 4550 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 6600 4450 50  0001 C CNN
F 3 "~" H 6600 4450 50  0001 C CNN
F 4 "C0402C222J3GEC7411" H 6600 4450 50  0001 C CNN "MPN"
F 5 "C1531" H 6600 4450 50  0001 C CNN "LCSC Part #"
	1    6600 4450
	-1   0    0    1   
$EndComp
NoConn ~ 5350 3050
Connection ~ 8100 800 
Wire Wire Line
	8100 800  7700 800 
Wire Wire Line
	8100 800  8355 800 
$Comp
L Device:C_Small C?
U 1 1 605E5E86
P 8100 900
AR Path="/5E2D92F4/605E5E86" Ref="C?"  Part="1" 
AR Path="/6062DC24/605E5E86" Ref="C35"  Part="1" 
F 0 "C35" V 8000 750 50  0000 L CNN
F 1 "4.7uF 50V" V 8200 700 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 8100 900 50  0001 C CNN
F 3 "~" H 8100 900 50  0001 C CNN
F 4 "HMK325C7475KN-TE" H 8100 900 50  0001 C CNN "MPN"
F 5 "" H 8100 900 50  0001 C CNN "LCSC Part #"
	1    8100 900 
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR?
U 1 1 5E398692
P 8100 1000
AR Path="/5E2D92F4/5E398692" Ref="#PWR?"  Part="1" 
AR Path="/6062DC24/5E398692" Ref="#PWR054"  Part="1" 
F 0 "#PWR054" H 8100 750 50  0001 C CNN
F 1 "GND" H 8105 827 50  0000 C CNN
F 2 "" H 8100 1000 50  0001 C CNN
F 3 "" H 8100 1000 50  0001 C CNN
	1    8100 1000
	1    0    0    -1  
$EndComp
$EndSCHEMATC
