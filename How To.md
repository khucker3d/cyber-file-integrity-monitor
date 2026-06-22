# How To: File Integrity Monitor (V1)

### Prep:
1. Download the Python [script](https://github.com/khucker3d/cyber-file-integrity-monitor/blob/main/file_integrity_monitor.py)
2. Verify/Install required dependencies via CLI: ```pip install watchdog```

   <img width="566" height="257" alt="Dependencies" src="https://github.com/user-attachments/assets/935c2f73-c11f-446a-bfff-bc4c22bc97e2" />


### Create Folder & Add Files:
3. Create a new folder called **"watched"**
4. Add the file(s) that will be monitored

   <img width="496" height="139" alt="1_SetupWatchFolderAndAddFile" src="https://github.com/user-attachments/assets/95110f79-2880-49ff-8d57-e67439876993" />


### Run Tool:
5. Open the script using the CLI command: 
   * Power Shell:```python file_integrity_monitor.py```
   * Terminal:```python3 file_integrity_monitor.py```

### Set Path:
6. Select the Browse button and point to the **"watched"** folder's location 

   <img width="899" height="120" alt="Path" src="https://github.com/user-attachments/assets/fe2ae21d-c0ee-4a80-8937-3c0e81149ab5" />


### Create the Baseline JSON
7. Ensure data files are finalized, approved, and in the correct folder location
8. Click **Create Baseline** and verify by reviewing the output

   <img width="441" height="19" alt="4_BaselineCreated" src="https://github.com/user-attachments/assets/6c269871-8665-42c3-8cfb-cdaee330aaa4" />

9. Ensure the ```fim_baseline.json``` file was generated 

   <img width="289" height="156" alt="JSONBaseCreated" src="https://github.com/user-attachments/assets/8a22d87f-bb57-47de-af95-c5833cd05733" />


### Start Monitoring
10. Click **Start Monitoring**

    <img width="899" height="409" alt="5_StartMonitering" src="https://github.com/user-attachments/assets/bc5fd41f-a0bb-4f17-8b57-ae299130d05f" />

11. In the Output, look for the tool scanning messages to verify

    <img width="672" height="42" alt="Screenshot 2026-06-21 at 20 55 19" src="https://github.com/user-attachments/assets/6d96ebd0-3f60-4114-9c90-638c8a4cb292" />

### Discovery & Escalation
12. When the file data has been changed:

   * File change will be indicated in the Dashboard Counters
   
     <img width="403" height="45" alt="Dashbard" src="https://github.com/user-attachments/assets/44eebe9c-1a15-49fe-a410-b26df875e19a" />
    
   * The changes will appear in red text
   
     <img width="386" height="41" alt="Change" src="https://github.com/user-attachments/assets/3dfb0837-324a-4ac8-9e87-a6cc4b9754e0" />


### Review Note: 
13. Submit a **Review Note** to capture in the Output that you observed the alert and escalating
    Example: Discovered LDAP Pswrd Change > Investigating

### File Actions: 
14. Once the solution is found and approved, choose the instructed response **Action**:

    <img width="528" height="208" alt="8_Opt1_1Revert_All_Change" src="https://github.com/user-attachments/assets/c5cc1592-40ff-4382-99ea-419ad62ad280" />
     
       _Once reverted, an output message will appear_
      
       <img width="819" height="49" alt="8_Opt1_2Revert_All_Change_ResultOutput" src="https://github.com/user-attachments/assets/a4d17dc8-b060-420a-95b6-28d47fdd8e00" />


#### Action Types:

<img width="898" height="119" alt="7_ActionsOptions" src="https://github.com/user-attachments/assets/74810bd9-e526-4cb1-9269-63cf906137d9" />

##### Approve Data: Approve All Changes
1. After verifying that the data changes were valid and no security action is needed, use the **Approve Data** button
2. Create a new Baseline and validate changes


##### Overwrite Data: Best for Individual Change
1. Enter the Field Label

    <img width="685" height="405" alt="8_Opt2_2Overwrite_Specific_Data_LDAP" src="https://github.com/user-attachments/assets/7d15946e-d69f-47a6-8c81-12b06072a0c8" />

2. Verify the path and label changes, and select **Yes**
   
    <img width="276" height="298" alt="8_Opt2_4Overwrite_Specific_Data_LDAP" src="https://github.com/user-attachments/assets/d82e91ea-4237-4c76-ac25-e7bdbb88566a" />

3. Enter the label change data
   
    <img width="592" height="198" alt="8_Opt2_3Overwrite_Specific_Data_LDAP" src="https://github.com/user-attachments/assets/8f763f32-a18b-4c6d-9889-5372c950dea8" />

##### Revert Changes: 
1. Select the **Revert Changes** button & Verify data reverted to trusted baseline
    <img width="528" height="208" alt="8_Opt1_1Revert_All_Change" src="https://github.com/user-attachments/assets/831c6105-3510-4433-b660-2076520869c8" />
    
    <img width="819" height="49" alt="8_Opt1_2Revert_All_Change_ResultOutput" src="https://github.com/user-attachments/assets/f78a5ff9-e380-42e1-ba77-25e700004827" />
   
2. Manually change the password to the temp IT password for user reset

#### Add (Resolution) Review Note:
15. Submit a **Review Note** to note in the Output of the protocol solution and the status of the investigation 
    Example: Discovered LDAP Pswrd Change > Investigated > Verified > Escilated > Protocol: 62-B > Action: Overwrite > Resolved    
  <img width="292" height="171" alt="LogNote" src="https://github.com/user-attachments/assets/ee3002b9-e493-4100-8220-118f3145a2ce" />

   _Once accepted, an output message will appear_
    <img width="816" height="25" alt="LogNoteOutput" src="https://github.com/user-attachments/assets/d36729c7-fbce-43eb-a46d-f8ffcf148200" />
