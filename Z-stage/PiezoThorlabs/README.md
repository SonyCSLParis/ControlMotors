# Coarse control of a piezo-controlled translation stage

Thorlabs provides a travel stage ([NFL5DP20](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=720&pn=NFL5DP20/M)) with a coarse manual translation range of 5 mm with possibility to 
actuate a fine transational movement with a piezo controller ([KPZ101](https://github.com/SonyCSLParis/Motorized-stage/blob/main/Z-stage/PiezoThorlabs/KPZ101.jpg)).  

![stage](https://github.com/SonyCSLParis/Motorized-stage/blob/main/Z-stage/PiezoThorlabs/translation_stage.jpg)
![piezo](https://github.com/SonyCSLParis/Motorized-stage/blob/main/Z-stage/PiezoThorlabs/KPZ101.jpg)  


The Thorabs translation stage translation movement controlled by a piezoelectric controller allows fine movements that could not be achieved with a stepper motor. However, the automated range of displacement of the stage is intrisically limited by the piezo, to 20 µm.   
We decided to automate the coarse control with a stepper motor connected to the manual differential micrometer drive via a belt-pulley system. the pulley was designed using the parametric pulley model provided [here](). We added holes to attach the piece to the differential drive part with screws.  

The part we designed has 55 teeth and can be found [here](https://github.com/SonyCSLParis/Motorized-stage/blob/main/Z-stage/PiezoThorlabs/z_focus_55_teeth_190.stl).  

![setup](https://user-images.githubusercontent.com/20478886/234916360-f88d8eee-468c-4019-a319-57cfc0e260fb.jpg)

The design requires to adjust the position of the motor pulley to keep the belt orthogonal to the drive rotation, and to firmly attach the stepper motor to the optcal bed.   

The Nema motor is controlled by ControlMotors code, according to the descripition here: https://github.com/SonyCSLParis/ControlMotors.   
